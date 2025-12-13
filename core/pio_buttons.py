import array

try:
    import adafruit_pioasm  # type: ignore
except ImportError:  # CircuitPython build sense (library not bundled)
    adafruit_pioasm = None  # pragma: no cover

import rp2pio


_BUTTON_PIO_TEMPLATE = """
.program button_watch
.wrap_target
loop:
    in pins, {pin_span}
    push block
    jmp loop
.wrap
"""


def _encode_in_pins(count):
    # opcode=IN (0b010), source=PINS (0), count in lower 5 bits
    return (0b010 << 13) | (0 << 5) | (count & 0x1F)


def _encode_push_block():
    # opcode=PUSH (0b100), block=1 (bit7), if_full=0
    return (0b100 << 13) | (1 << 7)


def _encode_jmp(target):
    # opcode=JMP (0b000), condition=always (0)
    return (0b000 << 13) | (target & 0x1F)


def _assemble_button_program(pin_span):
    if adafruit_pioasm is not None:
        program = adafruit_pioasm.assemble(
            _BUTTON_PIO_TEMPLATE.format(pin_span=pin_span)
        )
        instruction_count = len(program) // 2
        return program, 0, instruction_count - 1

    # Fallback: hand-assembled program equivalent to template above
    instructions = (
        _encode_in_pins(pin_span),
        _encode_push_block(),
        _encode_jmp(0),
    )
    program = bytearray()
    for instr in instructions:
        program.append(instr & 0xFF)
        program.append((instr >> 8) & 0xFF)
    return bytes(program), 0, len(instructions) - 1


class _ButtonGroup:
    __slots__ = (
        "state_machine",
        "base_pin_id",
        "bit_indices",
        "global_indices",
        "sample",
    )

    def __init__(
        self,
        state_machine,
        base_pin_id,
        bit_indices,
        global_indices,
    ):
        self.state_machine = state_machine
        self.base_pin_id = base_pin_id
        self.bit_indices = bit_indices
        self.global_indices = global_indices
        self.sample = 0


class _ButtonProxy:
    """Lightweight proxy that exposes the latest sampled value via ``.value``."""

    __slots__ = ("_manager", "_index")

    def __init__(self, manager, index):
        self._manager = manager
        self._index = index

    @property
    def value(self) -> bool:
        return self._manager.state[self._index]


class ButtonPIOManager:
    """Observa un conjunt de botons mitjançant PIO i exposa proxies compatibles.

    Es creen tantes màquines d'estat com grups contigus de pins. En detectar un
    canvi, el PIO envia el nou mostreig al FIFO i el gestor actualitza un cache
    en memòria, evitant canvis en el codi existent que consulta ``.value``.
    """

    def __init__(
        self,
        pins,
        *,
        frequency=1_000_000,
        pull_down=True,
    ):
        self._pins = list(pins)
        if not self._pins:
            raise ValueError("ButtonPIOManager requires at least one pin")

        self._state = [False] * len(self._pins)
        self._groups = []
        self._buffer = array.array("I", [0])

        # Construir grups de pins contigus (per id) per a cada màquina PIO.
        pins_with_id = []
        single_pin_groups = []
        for idx, pin in enumerate(self._pins):
            pin_id = getattr(pin, "id", None)
            if pin_id is None:
                single_pin_groups.append([(idx, idx, pin)])
            else:
                pins_with_id.append((pin_id, idx, pin))

        if pins_with_id:
            sorted_pin_data = sorted(pins_with_id, key=lambda item: item[0])

            current_group = []
            last_pin_id = None
            for pin_id, original_idx, pin in sorted_pin_data:
                if last_pin_id is None or pin_id == last_pin_id + 1:
                    current_group.append((pin_id, original_idx, pin))
                else:
                    self._groups.append(
                        self._create_group(current_group, frequency, pull_down)
                    )
                    current_group = [(pin_id, original_idx, pin)]
                last_pin_id = pin_id

            if current_group:
                self._groups.append(
                    self._create_group(current_group, frequency, pull_down)
                )

        for group in single_pin_groups:
            self._groups.append(
                self._create_group(group, frequency, pull_down)
            )

        # Desar proxies en ordre original.
        self._proxies = [_ButtonProxy(self, index) for index in range(len(self._pins))]

        # Assegurar que disposem de l'estat inicial.
        self.update()

    def _create_group(self, group_data, frequency, pull_down):
        base_pin_id, _, base_pin = group_data[0]
        bit_indices = [pin_id - base_pin_id for pin_id, _, _ in group_data]
        span = len(group_data)

        program, wrap_target, wrap = _assemble_button_program(span)

        sm = rp2pio.StateMachine(
            program=program,
            frequency=frequency,
            first_in_pin=base_pin,
            in_pin_count=span,
            pull_in_pin_down=pull_down,
            auto_push=False,
            push_threshold=32,
            wrap_target=wrap_target,
            wrap=wrap,
        )

        global_indices = [original_idx for _, original_idx, _ in group_data]
        return _ButtonGroup(sm, base_pin_id, bit_indices, global_indices)

    @property
    def state(self):
        return self._state

    @property
    def proxies(self):
        return self._proxies

    def create_proxy(self, index):
        return self._proxies[index]

    def update(self):
        """Llegeix les cues de totes les màquines i actualitza el cache."""
        any_update = False
        for group in self._groups:
            sm = group.state_machine
            while sm.in_waiting:
                sm.readinto(self._buffer)
                group.sample = self._buffer[0]
                any_update = True

                for bit_index, global_index in zip(
                    group.bit_indices, group.global_indices
                ):
                    self._state[global_index] = bool((group.sample >> bit_index) & 1)

        return any_update

    def deinit(self):
        for group in self._groups:
            group.state_machine.deinit()
