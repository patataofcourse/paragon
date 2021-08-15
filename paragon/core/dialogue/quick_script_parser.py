from paragon.core.dialogue.commands import SetConversationTypeCommand, LoadAssetsCommand, WaitCommand, \
    SetSpeakerCommand, SynchronizeCommand, PrintCommand, PauseCommand, NewlineCommand

from paragon.core.dialogue.scanner import ScannerError


def parse(dialogue: str, char1: str, char1_pos: int, char2: str, char2_pos: int):
    commands = [
        SetConversationTypeCommand(1),
        LoadAssetsCommand(char1, char1_pos),
        LoadAssetsCommand(char2, char2_pos),
        WaitCommand(0),
    ]
    speaker = None
    lines = dialogue.splitlines()
    for i, line in enumerate(lines):
        if stripped := line.strip():
            if stripped.startswith(char1 + ":"):
                current_char = char1
            elif stripped.startswith(char2 + ":"):
                current_char = char2
            else:
                raise ScannerError(stripped, i, "Line must start with a character name followed by ':'")
            parts = stripped.split(":", 1)
            new_speaker, new_text = current_char, parts[1].strip()
            if new_speaker != speaker:
                commands.extend([
                    SetSpeakerCommand(parts[0]),
                    SynchronizeCommand(),
                ])
            commands.extend([
                PrintCommand(new_text),
                PauseCommand(),
            ])
            if i < len(lines) - 1:
                commands.append(NewlineCommand())
    return commands