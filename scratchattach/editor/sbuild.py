from __future__ import annotations

from .. import editor
from typing import Optional

# Copied from sbuild so we have to make a few wrappers ;-;
# May need to recreate this from scratch. In which case, it is to be done in palette.py
class Block(editor.Block):
    ...

class Input(editor.Input):
    ...
class Field(editor.Field):
    ...
class Variable(editor.Variable):
    ...
class List(editor.List):
    ...
class Broadcast(editor.Broadcast):
    ...
class Mutation(editor.Mutation):
    ...


class Motion:
    class MoveSteps(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "motion_movesteps", _shadow=shadow, pos=pos)

        def set_steps(self, value, input_type: str | int = "number", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("STEPS", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class TurnRight(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "motion_turnright", _shadow=shadow, pos=pos)

        def set_degrees(self, value, input_type: str | int = "number", shadow_status: int = 1, *,
                        input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("DEGREES", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class TurnLeft(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "motion_turnleft", _shadow=shadow, pos=pos)

        def set_degrees(self, value, input_type: str | int = "number", shadow_status: int = 1, *,
                        input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("DEGREES", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class GoTo(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "motion_goto", _shadow=shadow, pos=pos)

        def set_to(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                   input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(Input("TO", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class GoToMenu(Block):
        def __init__(self, *, shadow: bool = True, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "motion_goto_menu", _shadow=shadow, pos=pos)

        def set_to(self, value: str = "_random_", value_id: Optional[str] = None):
            return self.add_field(Field("TO", value, value_id))

    class GoToXY(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "motion_gotoxy", _shadow=shadow, pos=pos)

        def set_x(self, value, input_type: str | int = "number", shadow_status: int = 1, *,
                  input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(Input("X", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_y(self, value, input_type: str | int = "number", shadow_status: int = 1, *,
                  input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(Input("Y", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class GlideTo(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "motion_glideto", _shadow=shadow, pos=pos)

        def set_secs(self, value, input_type: str | int = "positive number", shadow_status: int = 1, *,
                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(Input("SECS", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_to(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                   input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(Input("TO", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class GlideToMenu(Block):
        def __init__(self, *, shadow: bool = True, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "motion_glideto_menu", _shadow=shadow, pos=pos)

        def set_to(self, value: str = "_random_", value_id: Optional[str] = None):
            return self.add_field(Field("TO", value, value_id))

    class GlideSecsToXY(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "motion_glidesecstoxy", _shadow=shadow, pos=pos)

        def set_x(self, value, input_type: str | int = "number", shadow_status: int = 1, *,
                  input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(Input("X", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_y(self, value, input_type: str | int = "number", shadow_status: int = 1, *,
                  input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(Input("Y", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_secs(self, value, input_type: str | int = "positive number", shadow_status: int = 1, *,
                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(Input("SECS", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class PointInDirection(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "motion_pointindirection", _shadow=shadow, pos=pos)

        def set_direction(self, value, input_type: str | int = "angle", shadow_status: int = 1, *,
                          input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("DIRECTION", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class PointTowards(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "motion_pointtowards", _shadow=shadow, pos=pos)

        def set_towards(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                        input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("TOWARDS", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class PointTowardsMenu(Block):
        def __init__(self, *, shadow: bool = True, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "motion_pointtowards_menu", _shadow=shadow, pos=pos)

        def set_towards(self, value: str = "_mouse_", value_id: Optional[str] = None):
            return self.add_field(Field("TOWARDS", value, value_id))

    class ChangeXBy(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "motion_changexby", _shadow=shadow, pos=pos)

        def set_dx(self, value, input_type: str | int = "number", shadow_status: int = 1, *,
                   input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(Input("DX", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class ChangeYBy(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "motion_changeyby", _shadow=shadow, pos=pos)

        def set_dy(self, value, input_type: str | int = "number", shadow_status: int = 1, *,
                   input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(Input("DY", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class SetX(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "motion_setx", _shadow=shadow, pos=pos)

        def set_x(self, value, input_type: str | int = "number", shadow_status: int = 1, *,
                  input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(Input("X", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class SetY(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "motion_sety", _shadow=shadow, pos=pos)

        def set_y(self, value, input_type: str | int = "number", shadow_status: int = 1, *,
                  input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(Input("Y", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class IfOnEdgeBounce(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "motion_ifonedgebounce", _shadow=shadow, pos=pos)

    class SetRotationStyle(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "motion_setrotationstyle", _shadow=shadow, pos=pos)

        def set_style(self, value: str = "all around", value_id: Optional[str] = None):
            return self.add_field(Field("STYLE", value, value_id))

    class XPosition(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "motion_xposition", _shadow=shadow, pos=pos)

    class YPosition(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "motion_yposition", _shadow=shadow, pos=pos)

    class Direction(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "motion_direction", _shadow=shadow, pos=pos)

    class ScrollRight(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "motion_scroll_right", _shadow=shadow, pos=pos)

        def set_distance(self, value, input_type: str | int = "number", shadow_status: int = 1, *,
                         input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("DISTANCE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class ScrollUp(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "motion_scroll_up", _shadow=shadow, pos=pos)

        def set_distance(self, value, input_type: str | int = "number", shadow_status: int = 1, *,
                         input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("DISTANCE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class AlignScene(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "motion_align_scene", _shadow=shadow, pos=pos)

        def set_alignment(self, value: str = "bottom-left", value_id: Optional[str] = None):
            return self.add_field(Field("ALIGNMENT", value, value_id))

    class XScroll(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "motion_xscroll", _shadow=shadow, pos=pos)

    class YScroll(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "motion_yscroll", _shadow=shadow, pos=pos)


class Looks:
    class SayForSecs(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "looks_sayforsecs", _shadow=shadow, pos=pos)

        def set_message(self, value="Hello!", input_type: str | int = "string", shadow_status: int = 1, *,
                        input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("MESSAGE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer)
            )

        def set_secs(self, value=2, input_type: str | int = "positive integer", shadow_status: int = 1, *,
                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("SECS", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer)
            )

    class Say(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "looks_say", _shadow=shadow, pos=pos)

        def set_message(self, value="Hello!", input_type: str | int = "string", shadow_status: int = 1, *,
                        input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("MESSAGE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer)
            )

    class ThinkForSecs(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "looks_thinkforsecs", _shadow=shadow, pos=pos)

        def set_message(self, value="Hmm...", input_type: str | int = "string", shadow_status: int = 1, *,
                        input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("MESSAGE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer)
            )

        def set_secs(self, value=2, input_type: str | int = "positive integer", shadow_status: int = 1, *,
                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("SECS", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer)
            )

    class Think(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "looks_think", _shadow=shadow, pos=pos)

        def set_message(self, value="Hmm...", input_type: str | int = "string", shadow_status: int = 1, *,
                        input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("MESSAGE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer)
            )

    class SwitchCostumeTo(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "looks_switchcostumeto", _shadow=shadow, pos=pos)

        def set_costume(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                        input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("COSTUME", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class Costume(Block):
        def __init__(self, *, shadow: bool = True, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "looks_costume", _shadow=shadow, pos=pos)

        def set_costume(self, value: str = "costume1", value_id: Optional[str] = None):
            return self.add_field(Field("COSTUME", value, value_id))

    class NextCostume(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "looks_nextcostume", _shadow=shadow, pos=pos)

    class SwitchBackdropTo(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "looks_switchbackdropto", _shadow=shadow, pos=pos)

        def set_backdrop(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                         input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("BACKDROP", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class Backdrops(Block):
        def __init__(self, *, shadow: bool = True, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "looks_backdrops", _shadow=shadow, pos=pos)

        def set_backdrop(self, value: str = "costume1", value_id: Optional[str] = None):
            return self.add_field(Field("BACKDROP", value, value_id))

    class SwitchBackdropToAndWait(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "looks_switchbackdroptoandwait", _shadow=shadow, pos=pos)

        def set_backdrop(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                         input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("BACKDROP", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class NextBackdrop(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "looks_nextbackdrop", _shadow=shadow, pos=pos)

    class ChangeSizeBy(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "looks_changesizeby", _shadow=shadow, pos=pos)

        def set_change(self, value="10", input_type: str | int = "number", shadow_status: int = 1, *,
                       input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("CHANGE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class SetSizeTo(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "looks_setsizeto", _shadow=shadow, pos=pos)

        def set_size(self, value="100", input_type: str | int = "number", shadow_status: int = 1, *,
                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("SIZE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class ChangeEffectBy(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "looks_changeeffectby", _shadow=shadow, pos=pos)

        def set_change(self, value="100", input_type: str | int = "number", shadow_status: int = 1, *,
                       input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("CHANGE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_effect(self, value: str = "COLOR", value_id: Optional[str] = None):
            return self.add_field(Field("EFFECT", value, value_id))

    class SetEffectTo(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "looks_seteffectto", _shadow=shadow, pos=pos)

        def set_value(self, value="0", input_type: str | int = "number", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("VALUE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_effect(self, value: str = "COLOR", value_id: Optional[str] = None):
            return self.add_field(Field("EFFECT", value, value_id))

    class ClearGraphicEffects(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "looks_cleargraphiceffects", _shadow=shadow, pos=pos)

    class Hide(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "looks_hide", _shadow=shadow, pos=pos)

    class Show(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "looks_show", _shadow=shadow, pos=pos)

    class GoToFrontBack(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "looks_gotofrontback", _shadow=shadow, pos=pos)

        def set_front_back(self, value: str = "front", value_id: Optional[str] = None):
            return self.add_field(Field("FRONT_BACK", value, value_id))

    class GoForwardBackwardLayers(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "looks_goforwardbackwardlayers", _shadow=shadow, pos=pos)

        def set_num(self, value="1", input_type: str | int = "positive integer", shadow_status: int = 1, *,
                    input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("NUM", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_fowrward_backward(self, value: str = "forward", value_id: Optional[str] = None):
            return self.add_field(Field("FORWARD_BACKWARD", value, value_id))

    class CostumeNumberName(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "looks_costumenumbername", _shadow=shadow, pos=pos)

        def set_number_name(self, value: str = "string", value_id: Optional[str] = None):
            return self.add_field(Field("NUMBER_NAME", value, value_id))

    class BackdropNumberName(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "looks_backdropnumbername", _shadow=shadow, pos=pos)

        def set_number_name(self, value: str = "number", value_id: Optional[str] = None):
            return self.add_field(Field("NUMBER_NAME", value, value_id))

    class Size(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "looks_size", _shadow=shadow, pos=pos)

    class HideAllSprites(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "looks_hideallsprites", _shadow=shadow, pos=pos)

    class SetStretchTo(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "looks_setstretchto", _shadow=shadow, pos=pos)

        def set_stretch(self, value="100", input_type: str | int = "number", shadow_status: int = 1, *,
                        input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("STRETCH", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class ChangeStretchBy(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "looks_changestretchby", _shadow=shadow, pos=pos)

        def set_change(self, value="10", input_type: str | int = "number", shadow_status: int = 1, *,
                       input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("CHANGE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))


class Sounds:
    class Play(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sound_play", _shadow=shadow, pos=pos)

        def set_sound_menu(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                           input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("SOUND_MENU", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class SoundsMenu(Block):
        def __init__(self, *, shadow: bool = True, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sound_sounds_menu", _shadow=shadow, pos=pos)

        def set_sound_menu(self, value: str = "pop", value_id: Optional[str] = None):
            return self.add_field(Field("SOUND_MENU", value, value_id))

    class PlayUntilDone(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sound_playuntildone", _shadow=shadow, pos=pos)

        def set_sound_menu(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                           input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("SOUND_MENU", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class StopAllSounds(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sound_stopallsounds", _shadow=shadow, pos=pos)

    class ChangeEffectBy(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sound_changeeffectby", _shadow=shadow, pos=pos)

        def set_value(self, value="10", input_type: str | int = "number", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("VALUE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_effect(self, value: str = "PITCH", value_id: Optional[str] = None):
            return self.add_field(Field("EFFECT", value, value_id))

    class SetEffectTo(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sound_seteffectto", _shadow=shadow, pos=pos)

        def set_value(self, value="100", input_type: str | int = "number", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("VALUE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_effect(self, value: str = "PITCH", value_id: Optional[str] = None):
            return self.add_field(Field("EFFECT", value, value_id))

    class ClearEffects(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sound_cleareffects", _shadow=shadow, pos=pos)

    class ChangeVolumeBy(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sound_changevolumeby", _shadow=shadow, pos=pos)

        def set_volume(self, value="-10", input_type: str | int = "number", shadow_status: int = 1, *,
                       input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("VOLUME", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class SetVolumeTo(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sound_setvolumeto", _shadow=shadow, pos=pos)

        def set_volume(self, value="100", input_type: str | int = "number", shadow_status: int = 1, *,
                       input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("VOLUME", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class Volume(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sound_volume", _shadow=shadow, pos=pos)


class Events:
    class WhenFlagClicked(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "event_whenflagclicked", _shadow=shadow, pos=pos)

    class WhenKeyPressed(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "event_whenkeypressed", _shadow=shadow, pos=pos)

        def set_key_option(self, value: str = "space", value_id: Optional[str] = None):
            return self.add_field(Field("KEY_OPTION", value, value_id))

    class WhenThisSpriteClicked(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "event_whenthisspriteclicked", _shadow=shadow, pos=pos)

    class WhenStageClicked(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "event_whenstageclicked", _shadow=shadow, pos=pos)

    class WhenBackdropSwitchesTo(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "event_whenbackdropswitchesto", _shadow=shadow, pos=pos)

        def set_backdrop(self, value: str = "backdrop1", value_id: Optional[str] = None):
            return self.add_field(Field("BACKDROP", value, value_id))

    class WhenGreaterThan(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "event_whengreaterthan", _shadow=shadow, pos=pos)

        def set_value(self, value="10", input_type: str | int = "number", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("VALUE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_when_greater_than_menu(self, value: str = "LOUDNESS", value_id: Optional[str] = None):
            return self.add_field(Field("WHENGREATERTHANMENU", value, value_id))

    class WhenBroadcastReceived(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "event_whenbroadcastreceived", _shadow=shadow, pos=pos)

        def set_broadcast_option(self, value="message1", value_id: str = "I didn't get an id..."):
            return self.add_field(Field("BROADCAST_OPTION", value, value_id))

    class Broadcast(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "event_broadcast", _shadow=shadow, pos=pos)

        def set_broadcast_input(self, value="message1", input_type: str | int = "broadcast", shadow_status: int = 1, *,
                                input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("BROADCAST_INPUT", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class BroadcastAndWait(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "event_broadcastandwait", _shadow=shadow, pos=pos)

        def set_broadcast_input(self, value="message1", input_type: str | int = "broadcast", shadow_status: int = 1, *,
                                input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("BROADCAST_INPUT", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class WhenTouchingObject(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "event_whentouchingobject", _shadow=shadow, pos=pos)

        def set_touching_object_menu(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("TOUCHINGOBJECTMENU", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class TouchingObjectMenu(Block):
        def __init__(self, *, shadow: bool = True, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "event_touchingobjectmenu", _shadow=shadow, pos=pos)

        def set_touching_object_menu(self, value: str = "_mouse_", value_id: Optional[str] = None):
            return self.add_field(Field("TOUCHINGOBJECTMENU", value, value_id))


class Control:
    class Wait(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "control_wait", _shadow=shadow, pos=pos)

        def set_duration(self, value="1", input_type: str | int = "number", shadow_status: int = 1, *,
                         input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("DURATION", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class Forever(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "control_forever", _shadow=shadow, pos=pos, can_next=False)

        def set_substack(self, value, input_type: str | int = "block", shadow_status: int = 2, *,
                         input_id: Optional[str] = None):
            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            inp = Input("SUBSTACK", value, input_type, shadow_status, input_id=input_id)
            return self.add_input(inp)

    class If(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "control_if", _shadow=shadow, pos=pos)

        def set_substack(self, value, input_type: str | int = "block", shadow_status: int = 2, *,
                         input_id: Optional[str] = None):
            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            inp = Input("SUBSTACK", value, input_type, shadow_status, input_id=input_id)
            return self.add_input(inp)

        def set_condition(self, value, input_type: str | int = "block", shadow_status: int = 2, *,
                          input_id: Optional[str] = None):
            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            inp = Input("CONDITION", value, input_type, shadow_status, input_id=input_id)
            return self.add_input(inp)

    class IfElse(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "control_if_else", _shadow=shadow, pos=pos)

        def set_substack1(self, value, input_type: str | int = "block", shadow_status: int = 2, *,
                          input_id: Optional[str] = None):
            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            inp = Input("SUBSTACK", value, input_type, shadow_status, input_id=input_id)
            return self.add_input(inp)

        def set_substack2(self, value, input_type: str | int = "block", shadow_status: int = 2, *,
                          input_id: Optional[str] = None):
            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            inp = Input("SUBSTACK2", value, input_type, shadow_status, input_id=input_id)
            return self.add_input(inp)

        def set_condition(self, value, input_type: str | int = "block", shadow_status: int = 2, *,
                          input_id: Optional[str] = None):
            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            inp = Input("CONDITION", value, input_type, shadow_status, input_id=input_id)
            return self.add_input(inp)

    class WaitUntil(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "control_wait_until", _shadow=shadow, pos=pos)

        def set_condition(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                          input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("CONDITION", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class RepeatUntil(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "control_repeat_until", _shadow=shadow, pos=pos)

        def set_substack(self, value, input_type: str | int = "block", shadow_status: int = 2, *,
                         input_id: Optional[str] = None):
            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            inp = Input("SUBSTACK", value, input_type, shadow_status, input_id=input_id)
            return self.add_input(inp)

        def set_condition(self, value, input_type: str | int = "block", shadow_status: int = 2, *,
                          input_id: Optional[str] = None):
            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            inp = Input("CONDITION", value, input_type, shadow_status, input_id=input_id)
            return self.add_input(inp)

    class While(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "control_while", _shadow=shadow, pos=pos)

        def set_substack(self, value, input_type: str | int = "block", shadow_status: int = 2, *,
                         input_id: Optional[str] = None):
            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            inp = Input("SUBSTACK", value, input_type, shadow_status, input_id=input_id)
            return self.add_input(inp)

        def set_condition(self, value, input_type: str | int = "block", shadow_status: int = 2, *,
                          input_id: Optional[str] = None):
            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            inp = Input("CONDITION", value, input_type, shadow_status, input_id=input_id)
            return self.add_input(inp)

    class Stop(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "control_stop", _shadow=shadow, pos=pos, mutation=Mutation())

        def set_stop_option(self, value: str = "all", value_id: Optional[str] = None):
            return self.add_field(Field("STOP_OPTION", value, value_id))

        def set_hasnext(self, has_next: bool = True):
            self.mutation.has_next = has_next
            return self

    class StartAsClone(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "control_start_as_clone", _shadow=shadow, pos=pos)

    class CreateCloneOf(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "control_create_clone_of", _shadow=shadow, pos=pos)

        def set_clone_option(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                             input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("CLONE_OPTION", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class CreateCloneOfMenu(Block):
        def __init__(self, *, shadow: bool = True, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "control_create_clone_of_menu", _shadow=shadow, pos=pos)

        def set_clone_option(self, value: str = "_myself_", value_id: Optional[str] = None):
            return self.add_field(Field("CLONE_OPTION", value, value_id))

    class DeleteThisClone(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "control_delete_this_clone", _shadow=shadow, pos=pos, can_next=False)

    class ForEach(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "control_for_each", _shadow=shadow, pos=pos)

        def set_substack(self, value, input_type: str | int = "block", shadow_status: int = 2, *,
                         input_id: Optional[str] = None):
            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            inp = Input("SUBSTACK", value, input_type, shadow_status, input_id=input_id)
            return self.add_input(inp)

        def set_value(self, value="5", input_type: str | int = "positive integer", shadow_status: int = 1, *,
                      input_id: Optional[str] = None):
            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            inp = Input("VALUE", value, input_type, shadow_status, input_id=input_id)
            return self.add_input(inp)

        def set_variable(self, value: str = "i", value_id: Optional[str] = None):
            return self.add_field(Field("VARIABLE", value, value_id))

    class GetCounter(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "control_get_counter", _shadow=shadow, pos=pos)

    class IncrCounter(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "control_incr_counter", _shadow=shadow, pos=pos)

    class ClearCounter(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "control_clear_counter", _shadow=shadow, pos=pos)

    class AllAtOnce(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "control_all_at_once", _shadow=shadow, pos=pos)

        def set_substack(self, value, input_type: str | int = "block", shadow_status: int = 2, *,
                         input_id: Optional[str] = None):
            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            inp = Input("SUBSTACK", value, input_type, shadow_status, input_id=input_id)
            return self.add_input(inp)


class Sensing:
    class TouchingObject(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sensing_touchingobject", _shadow=shadow, pos=pos)

        def set_touching_object_menu(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("TOUCHINGOBJECTMENU", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class TouchingObjectMenu(Block):
        def __init__(self, *, shadow: bool = True, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sensing_touchingobjectmenu", _shadow=shadow, pos=pos)

        def set_touching_object_menu(self, value: str = "_mouse_", value_id: Optional[str] = None):
            return self.add_field(Field("TOUCHINGOBJECTMENU", value, value_id))

    class TouchingColor(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sensing_touchingcolor", _shadow=shadow, pos=pos)

        def set_color(self, value="#0000FF", input_type: str | int = "color", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("COLOR", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class ColorIsTouchingColor(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sensing_coloristouchingcolor", _shadow=shadow, pos=pos)

        def set_color1(self, value="#0000FF", input_type: str | int = "color", shadow_status: int = 1, *,
                       input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("COLOR", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_color2(self, value="#00FF00", input_type: str | int = "color", shadow_status: int = 1, *,
                       input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("COLOR2", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class DistanceTo(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sensing_distanceto", _shadow=shadow, pos=pos)

        def set_distance_to_menu(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                                 input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("DISTANCETOMENU", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class DistanceToMenu(Block):
        def __init__(self, *, shadow: bool = True, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sensing_distancetomenu", _shadow=shadow, pos=pos)

        def set_distance_to_menu(self, value: str = "_mouse_", value_id: Optional[str] = None):
            return self.add_field(Field("DISTANCETOMENU", value, value_id))

    class Loud(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sensing_loud", _shadow=shadow, pos=pos)

    class AskAndWait(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sensing_askandwait", _shadow=shadow, pos=pos)

        def set_question(self, value="What's your name?", input_type: str | int = "string", shadow_status: int = 1, *,
                         input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("QUESTION", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer)
            )

    class Answer(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sensing_answer", _shadow=shadow, pos=pos)

    class KeyPressed(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sensing_keypressed", _shadow=shadow, pos=pos)

        def set_key_option(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                           input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("KEY_OPTION", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class KeyOptions(Block):
        def __init__(self, *, shadow: bool = True, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sensing_keyoptions", _shadow=shadow, pos=pos)

        def set_key_option(self, value: str = "space", value_id: Optional[str] = None):
            return self.add_field(Field("KEY_OPTION", value, value_id))

    class MouseDown(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sensing_mousedown", _shadow=shadow, pos=pos)

    class MouseX(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sensing_mousex", _shadow=shadow, pos=pos)

    class MouseY(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sensing_mousey", _shadow=shadow, pos=pos)

    class SetDragMode(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sensing_setdragmode", _shadow=shadow, pos=pos)

        def set_drag_mode(self, value: str = "draggable", value_id: Optional[str] = None):
            return self.add_field(Field("DRAG_MODE", value, value_id))

    class Loudness(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sensing_loudness", _shadow=shadow, pos=pos)

    class Timer(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sensing_timer", _shadow=shadow, pos=pos)

    class ResetTimer(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sensing_resettimer", _shadow=shadow, pos=pos)

    class Of(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sensing_of", _shadow=shadow, pos=pos)

        def set_object(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                       input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("OBJECT", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_property(self, value: str = "backdrop #", value_id: Optional[str] = None):
            return self.add_field(Field("PROPERTY", value, value_id))

    class OfObjectMenu(Block):
        def __init__(self, *, shadow: bool = True, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sensing_of_object_menu", _shadow=shadow, pos=pos)

        def set_object(self, value: str = "_stage_", value_id: Optional[str] = None):
            return self.add_field(Field("OBJECT", value, value_id))

    class Current(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sensing_current", _shadow=shadow, pos=pos)

        def set_current_menu(self, value: str = "YEAR", value_id: Optional[str] = None):
            return self.add_field(Field("CURRENTMENU", value, value_id))

    class DaysSince2000(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sensing_dayssince2000", _shadow=shadow, pos=pos)

    class Username(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sensing_username", _shadow=shadow, pos=pos)

    class UserID(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "sensing_userid", _shadow=shadow, pos=pos)


class Operators:
    class Add(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "operator_add", _shadow=shadow, pos=pos)

        def set_num1(self, value='', input_type: str | int = "number", shadow_status: int = 1, *,
                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("NUM1", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_num2(self, value='', input_type: str | int = "number", shadow_status: int = 1, *,
                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("NUM2", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class Subtract(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "operator_subtract", _shadow=shadow, pos=pos)

        def set_num1(self, value='', input_type: str | int = "number", shadow_status: int = 1, *,
                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("NUM1", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_num2(self, value='', input_type: str | int = "number", shadow_status: int = 1, *,
                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("NUM2", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class Multiply(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "operator_multiply", _shadow=shadow, pos=pos)

        def set_num1(self, value='', input_type: str | int = "number", shadow_status: int = 1, *,
                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("NUM1", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_num2(self, value='', input_type: str | int = "number", shadow_status: int = 1, *,
                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("NUM2", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class Divide(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "operator_divide", _shadow=shadow, pos=pos)

        def set_num1(self, value='', input_type: str | int = "number", shadow_status: int = 1, *,
                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("NUM1", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_num2(self, value='', input_type: str | int = "number", shadow_status: int = 1, *,
                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("NUM2", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class Random(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "operator_random", _shadow=shadow, pos=pos)

        def set_from(self, value="1", input_type: str | int = "number", shadow_status: int = 1, *,
                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("FROM", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_to(self, value="10", input_type: str | int = "number", shadow_status: int = 1, *,
                   input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("TO", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class GT(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "operator_gt", _shadow=shadow, pos=pos)

        def set_operand1(self, value='', input_type: str | int = "number", shadow_status: int = 1, *,
                         input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("OPERAND1", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_operand2(self, value='', input_type: str | int = "number", shadow_status: int = 1, *,
                         input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("OPERAND2", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class LT(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "operator_lt", _shadow=shadow, pos=pos)

        def set_operand1(self, value='', input_type: str | int = "number", shadow_status: int = 1, *,
                         input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("OPERAND1", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_operand2(self, value='', input_type: str | int = "number", shadow_status: int = 1, *,
                         input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("OPERAND2", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class Equals(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "operator_equals", _shadow=shadow, pos=pos)

        def set_operand1(self, value='', input_type: str | int = "number", shadow_status: int = 1, *,
                         input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("OPERAND1", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_operand2(self, value='', input_type: str | int = "number", shadow_status: int = 1, *,
                         input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("OPERAND2", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class And(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "operator_and", _shadow=shadow, pos=pos)

        def set_operand1(self, value='', input_type: str | int = "number", shadow_status: int = 1, *,
                         input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("OPERAND1", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_operand2(self, value='', input_type: str | int = "number", shadow_status: int = 1, *,
                         input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("OPERAND2", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class Or(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "operator_or", _shadow=shadow, pos=pos)

        def set_operand1(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                         input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("OPERAND1", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_operand2(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                         input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("OPERAND2", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class Not(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "operator_not", _shadow=shadow, pos=pos)

        def set_operand(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                        input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("OPERAND", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class Join(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "operator_join", _shadow=shadow, pos=pos)

        def set_string1(self, value="apple ", input_type: str | int = "string", shadow_status: int = 1, *,
                        input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("STRING1", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_string2(self, value="banana", input_type: str | int = "string", shadow_status: int = 1, *,
                        input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("STRING2", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class LetterOf(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "operator_letter_of", _shadow=shadow, pos=pos)

        def set_letter(self, value="1", input_type: str | int = "positive integer", shadow_status: int = 1, *,
                       input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("LETTER", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_string(self, value="apple", input_type: str | int = "string", shadow_status: int = 1, *,
                       input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("STRING", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class Length(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "operator_length", _shadow=shadow, pos=pos)

        def set_string(self, value="apple", input_type: str | int = "string", shadow_status: int = 1, *,
                       input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("STRING", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class Contains(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "operator_contains", _shadow=shadow, pos=pos)

        def set_string1(self, value="apple", input_type: str | int = "string", shadow_status: int = 1, *,
                        input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("STRING1", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_string2(self, value="a", input_type: str | int = "string", shadow_status: int = 1, *,
                        input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("STRING2", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class Mod(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "operator_mod", _shadow=shadow, pos=pos)

        def set_num1(self, value='', input_type: str | int = "number", shadow_status: int = 1, *,
                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("NUM1", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_num2(self, value='', input_type: str | int = "number", shadow_status: int = 1, *,
                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("NUM2", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class Round(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "operator_round", _shadow=shadow, pos=pos)

        def set_num(self, value='', input_type: str | int = "number", shadow_status: int = 1, *,
                    input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("NUM", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class MathOp(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "operator_mathop", _shadow=shadow, pos=pos)

        def set_num(self, value='', input_type: str | int = "number", shadow_status: int = 1, *,
                    input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("NUM", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_operator(self, value: str = "abs", value_id: Optional[str] = None):
            return self.add_field(Field("OPERATOR", value, value_id))


class Data:
    class VariableArr(Block):
        def __init__(self, value, input_type: str | int = "variable", shadow_status: Optional[int] = None, *,
                     pos: tuple[int | float, int | float] = (0, 0)):
            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            inp = Input(None, value, input_type, shadow_status)
            if inp.type_str == "block":
                arr = inp.json[0]
            else:
                arr = inp.json[1][-1]

            super().__init__(array=arr, pos=pos)

    class Variable(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "data_variable", _shadow=shadow, pos=pos)

        def set_variable(self, value: str | Variable = "variable", value_id: Optional[str] = None):
            return self.add_field(Field("VARIABLE", value, value_id))

    class SetVariableTo(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "data_setvariableto", _shadow=shadow, pos=pos)

        def set_value(self, value="0", input_type: str | int = "string", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("VALUE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_variable(self, value: str | Variable = "variable", value_id: Optional[str] = None):
            return self.add_field(Field("VARIABLE", value, value_id))

    class ChangeVariableBy(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "data_changevariableby", _shadow=shadow, pos=pos)

        def set_value(self, value="1", input_type: str | int = "number", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("VALUE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_variable(self, value: str | Variable = "variable", value_id: Optional[str] = None):
            return self.add_field(Field("VARIABLE", value, value_id))

    class ShowVariable(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "data_showvariable", _shadow=shadow, pos=pos)

        def set_variable(self, value: str | Variable = "variable", value_id: Optional[str] = None):
            return self.add_field(Field("VARIABLE", value, value_id))

    class HideVariable(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "data_hidevariable", _shadow=shadow, pos=pos)

        def set_variable(self, value: str | Variable = "variable", value_id: Optional[str] = None):
            return self.add_field(Field("VARIABLE", value, value_id))

    class ListArr(Block):
        def __init__(self, value, input_type: str | int = "list", shadow_status: Optional[int] = None, *,
                     pos: tuple[int | float, int | float] = (0, 0)):
            inp = Input(None, value, input_type, shadow_status)
            if inp.type_str == "block":
                arr = inp.json[0]
            else:
                arr = inp.json[1][-1]

            super().__init__(array=arr, pos=pos)

    class ListContents(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "data_listcontents", _shadow=shadow, pos=pos)

        def set_list(self, value: str | List = "my list", value_id: Optional[str] = None):
            return self.add_field(Field("LIST", value, value_id))

    class AddToList(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "data_addtolist", _shadow=shadow, pos=pos)

        def set_item(self, value="thing", input_type: str | int = "string", shadow_status: int = 1, *,
                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("ITEM", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_list(self, value: str | List = "list", value_id: Optional[str] = None):
            return self.add_field(Field("LIST", value, value_id))

    class DeleteOfList(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "data_deleteoflist", _shadow=shadow, pos=pos)

        def set_index(self, value="random", input_type: str | int = "positive integer", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("INDEX", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_list(self, value: str | List = "list", value_id: Optional[str] = None):
            return self.add_field(Field("LIST", value, value_id))

    class InsertAtList(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "data_insertatlist", _shadow=shadow, pos=pos)

        def set_item(self, value="thing", input_type: str | int = "string", shadow_status: int = 1, *,
                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("ITEM", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_index(self, value="random", input_type: str | int = "positive integer", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("INDEX", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_list(self, value: str | List = "list", value_id: Optional[str] = None):
            return self.add_field(Field("LIST", value, value_id))

    class DeleteAllOfList(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "data_deletealloflist", _shadow=shadow, pos=pos)

        def set_list(self, value: str | List = "list", value_id: Optional[str] = None):
            return self.add_field(Field("LIST", value, value_id))

    class ReplaceItemOfList(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "data_replaceitemoflist", _shadow=shadow, pos=pos)

        def set_item(self, value="thing", input_type: str | int = "string", shadow_status: int = 1, *,
                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("ITEM", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_index(self, value="random", input_type: str | int = "positive integer", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("INDEX", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_list(self, value: str | List = "list", value_id: Optional[str] = None):
            return self.add_field(Field("LIST", value, value_id))

    class ItemOfList(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "data_itemoflist", _shadow=shadow, pos=pos)

        def set_index(self, value="random", input_type: str | int = "positive integer", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("INDEX", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_list(self, value: str | List = "list", value_id: Optional[str] = None):
            return self.add_field(Field("LIST", value, value_id))

    class ItemNumOfList(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "data_itemnumoflist", _shadow=shadow, pos=pos)

        def set_item(self, value="thing", input_type: str | int = "string", shadow_status: int = 1, *,
                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("ITEM", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_list(self, value: str | List = "list", value_id: Optional[str] = None):
            return self.add_field(Field("LIST", value, value_id))

    class LengthOfList(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "data_lengthoflist", _shadow=shadow, pos=pos)

        def set_list(self, value: str | List = "list", value_id: Optional[str] = None):
            return self.add_field(Field("LIST", value, value_id))

    class ListContainsItem(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "data_listcontainsitem", _shadow=shadow, pos=pos)

        def set_item(self, value="thing", input_type: str | int = "string", shadow_status: int = 1, *,
                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("ITEM", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_list(self, value: str | List = "list", value_id: Optional[str] = None):
            return self.add_field(Field("LIST", value, value_id))

    class ShowList(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "data_showlist", _shadow=shadow, pos=pos)

        def set_list(self, value: str | List = "list", value_id: Optional[str] = None):
            return self.add_field(Field("LIST", value, value_id))

    class HideList(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "data_hidelist", _shadow=shadow, pos=pos)

        def set_list(self, value: str | List = "list", value_id: Optional[str] = None):
            return self.add_field(Field("LIST", value, value_id))

    class ListIndexAll(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "data_listindexall", _shadow=shadow, pos=pos)

    class ListIndexRandom(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "data_listindexrandom", _shadow=shadow, pos=pos)


class Proc:
    class Definition(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "procedures_definition", _shadow=shadow, pos=pos)

        def set_custom_block(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                             input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("custom_block", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class Call(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "procedures_call", _shadow=shadow, pos=pos, mutation=Mutation())

        def set_proc_code(self, proc_code: str = ''):
            self.mutation.proc_code = proc_code
            return self

        def set_argument_ids(self, *argument_ids: list[str]):
            self.mutation.argument_ids = argument_ids
            return self

        def set_warp(self, warp: bool = True):
            self.mutation.warp = warp
            return self

        def set_arg(self, arg, value='', input_type: str | int = "string", shadow_status: int = 1, *,
                    input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input(arg, value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class Declaration(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "procedures_declaration", _shadow=shadow, pos=pos, mutation=Mutation())

        def set_proc_code(self, proc_code: str = ''):
            self.mutation.proc_code = proc_code
            return self

    class Prototype(Block):
        def __init__(self, *, shadow: bool = True, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "procedures_prototype", _shadow=shadow, pos=pos, mutation=Mutation())

        def set_proc_code(self, proc_code: str = ''):
            self.mutation.proc_code = proc_code
            return self

        def set_argument_ids(self, *argument_ids: list[str]):
            self.mutation.argument_ids = argument_ids
            return self

        def set_argument_names(self, *argument_names: list[str]):
            self.mutation.argument_names = list(argument_names)
            return self

        def set_argument_defaults(self, *argument_defaults: list[str]):
            self.mutation.argument_defaults = argument_defaults
            return self

        def set_warp(self, warp: bool = True):
            self.mutation.warp = warp
            return self

        def set_arg(self, arg, value, input_type: str | int = "block", shadow_status: int = 1, *,
                    input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input(arg, value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))


class Args:
    class EditorBoolean(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "argument_editor_boolean", _shadow=shadow, pos=pos, mutation=Mutation())

        def set_text(self, value: str = "foo", value_id: Optional[str] = None):
            return self.add_field(Field("TEXT", value, value_id))

    class EditorStringNumber(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "argument_editor_string_number", _shadow=shadow, pos=pos, mutation=Mutation())

        def set_text(self, value: str = "foo", value_id: Optional[str] = None):
            return self.add_field(Field("TEXT", value, value_id))

    class ReporterBoolean(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "argument_reporter_boolean", _shadow=shadow, pos=pos, mutation=Mutation())

        def set_value(self, value: str = "boolean", value_id: Optional[str] = None):
            return self.add_field(Field("VALUE", value, value_id))

    class ReporterStringNumber(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "argument_reporter_string_number", _shadow=shadow, pos=pos, mutation=Mutation())

        def set_value(self, value: str = "boolean", value_id: Optional[str] = None):
            return self.add_field(Field("VALUE", value, value_id))


class Addons:
    class IsTurbowarp(Args.ReporterBoolean):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(_shadow=shadow, pos=pos)
            self.set_value("is turbowarp?")

    class IsCompiled(Args.ReporterBoolean):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(_shadow=shadow, pos=pos)
            self.set_value("is compiled?")

    class IsForkphorus(Args.ReporterBoolean):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(_shadow=shadow, pos=pos)
            self.set_value("is forkphorus?")

    class Breakpoint(Proc.Call):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(_shadow=shadow, pos=pos)
            self.set_proc_code("​​breakpoint​​")

    class Log(Proc.Call):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(_shadow=shadow, pos=pos)
            self.set_proc_code("​​log​​ %s")
            self.set_argument_ids("arg0")

        def set_message(self, value='', input_type: str | int = "string", shadow_status: int = 1, *,
                        input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):
            return self.set_arg("arg0", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer)

    class Warn(Proc.Call):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(_shadow=shadow, pos=pos)
            self.set_proc_code("​​warn​​ %s")
            self.set_argument_ids("arg0")

        def set_message(self, value='', input_type: str | int = "string", shadow_status: int = 1, *,
                        input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):
            return self.set_arg("arg0", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer)

    class Error(Proc.Call):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(_shadow=shadow, pos=pos)
            self.set_proc_code("​​error​​ %s")
            self.set_argument_ids("arg0")

        def set_message(self, value='', input_type: str | int = "string", shadow_status: int = 1, *,
                        input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):
            return self.set_arg("arg0", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer)


class Pen:
    class Clear(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "pen_clear", _shadow=shadow, pos=pos)

    class Stamp(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "pen_stamp", _shadow=shadow, pos=pos)

    class PenDown(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "pen_penDown", _shadow=shadow, pos=pos)

    class PenUp(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "pen_penUp", _shadow=shadow, pos=pos)

    class SetPenColorToColor(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "pen_setPenColorToColor", _shadow=shadow, pos=pos)

        def set_color(self, value="#FF0000", input_type: str | int = "color", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("COLOR", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class ChangePenParamBy(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "pen_changePenColorParamBy", _shadow=shadow, pos=pos)

        def set_param(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("COLOR_PARAM", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_value(self, value="10", input_type: str | int = "number", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("VALUE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class SetPenParamTo(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "pen_setPenColorParamTo", _shadow=shadow, pos=pos)

        def set_param(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("COLOR_PARAM", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_value(self, value="10", input_type: str | int = "number", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("VALUE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class ChangePenSizeBy(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "pen_changePenSizeBy", _shadow=shadow, pos=pos)

        def set_size(self, value="1", input_type: str | int = "positive number", shadow_status: int = 1, *,
                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("SIZE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class SetPenSizeTo(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "pen_setPenSizeTo", _shadow=shadow, pos=pos)

        def set_size(self, value="1", input_type: str | int = "positive number", shadow_status: int = 1, *,
                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("SIZE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class SetPenHueTo(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "pen_setPenHueToNumber", _shadow=shadow, pos=pos)

        def set_hue(self, value="1", input_type: str | int = "positive number", shadow_status: int = 1, *,
                    input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("HUE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class ChangePenHueBy(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "pen_changePenHueBy", _shadow=shadow, pos=pos)

        def set_hue(self, value="1", input_type: str | int = "positive number", shadow_status: int = 1, *,
                    input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("HUE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class SetPenShadeTo(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "pen_setPenShadeToNumber", _shadow=shadow, pos=pos)

        def set_shade(self, value="1", input_type: str | int = "positive number", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("SHADE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class ChangePenShadeBy(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "pen_changePenShadeBy", _shadow=shadow, pos=pos)

        def set_shade(self, value="1", input_type: str | int = "positive number", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("SHADE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class ColorParamMenu(Block):
        def __init__(self, *, shadow: bool = True, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "pen_menu_colorParam", _shadow=shadow, pos=pos)

        def set_color_param(self, value: str = "color", value_id: Optional[str] = None):
            return self.add_field(Field("colorParam", value, value_id))


class Music:
    class PlayDrumForBeats(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "music_playDrumForBeats", _shadow=shadow, pos=pos)

        def set_drum(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("DRUM", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_beats(self, value="0.25", input_type: str | int = "positive number", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("BEATS", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class PlayNoteForBeats(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "music_playDrumForBeats", _shadow=shadow, pos=pos)

        def set_note(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("NOTE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_beats(self, value="0.25", input_type: str | int = "positive number", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("BEATS", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class RestForBeats(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "music_restForBeats", _shadow=shadow, pos=pos)

        def set_beats(self, value="0.25", input_type: str | int = "positive number", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("BEATS", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class SetTempo(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "music_setTempo", _shadow=shadow, pos=pos)

        def set_beats(self, value="60", input_type: str | int = "positive number", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("TEMPO", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class ChangeTempo(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "music_changeTempo", _shadow=shadow, pos=pos)

        def set_beats(self, value="60", input_type: str | int = "positive number", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("TEMPO", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class GetTempo(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "music_getTempo", _shadow=shadow, pos=pos)

    class SetInstrument(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "music_setInstrument", _shadow=shadow, pos=pos)

        def set_instrument(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                           input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("INSTRUMENT", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class MidiPlayDrumForBeats(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "music_midiPlayDrumForBeats", _shadow=shadow, pos=pos)

        def set_drum(self, value="123", input_type: str | int = "positive integer", shadow_status: int = 1, *,
                     input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("DRUM", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_beats(self, value="1", input_type: str | int = "positive number", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("BEATS", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class MidiSetInstrument(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "music_midiSetInstrument", _shadow=shadow, pos=pos)

        def set_instrument(self, value="6", input_type: str | int = "positive integer", shadow_status: int = 1, *,
                           input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("INSTRUMENT", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class MenuDrum(Block):
        def __init__(self, *, shadow: bool = True, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "music_menu_DRUM", _shadow=shadow, pos=pos)

        def set_drum(self, value: str = "1", value_id: Optional[str] = None):
            return self.add_field(Field("DRUM", value, value_id))

    class MenuInstrument(Block):
        def __init__(self, *, shadow: bool = True, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "music_menu_INSTRUMENT", _shadow=shadow, pos=pos)

        def set_instrument(self, value: str = "1", value_id: Optional[str] = None):
            return self.add_field(Field("INSTRUMENT", value, value_id))


class VideoSensing:
    class WhenMotionGreaterThan(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "videoSensing_whenMotionGreaterThan", _shadow=shadow, pos=pos)

        def set_reference(self, value="10", input_type: str | int = "number", shadow_status: int = 1, *,
                          input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("REFERENCE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class VideoOn(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "videoSensing_videoOn", _shadow=shadow, pos=pos)

        def set_attribute(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                          input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("ATTRIBUTE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_subject(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                        input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("SUBJECT", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class MenuAttribute(Block):
        def __init__(self, *, shadow: bool = True, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "videoSensing_menu_ATTRIBUTE", _shadow=shadow, pos=pos)

        def set_attribute(self, value: str = "motion", value_id: Optional[str] = None):
            return self.add_field(Field("ATTRIBUTE", value, value_id))

    class MenuSubject(Block):
        def __init__(self, *, shadow: bool = True, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "videoSensing_menu_SUBJECT", _shadow=shadow, pos=pos)

        def set_subject(self, value: str = "this sprite", value_id: Optional[str] = None):
            return self.add_field(Field("SUBJECT", value, value_id))

    class VideoToggle(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "videoSensing_videoToggle", _shadow=shadow, pos=pos)

        def set_video_state(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                            input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("VIDEO_STATE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class MenuVideoState(Block):
        def __init__(self, *, shadow: bool = True, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "videoSensing_menu_VIDEO_STATE", _shadow=shadow, pos=pos)

        def set_video_state(self, value: str = "on", value_id: Optional[str] = None):
            return self.add_field(Field("VIDEO_STATE", value, value_id))

    class SetVideoTransparency(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "videoSensing_setVideoTransparency", _shadow=shadow, pos=pos)

        def set_transparency(self, value: str = "50", input_type: str | int = "number", shadow_status: int = 1, *,
                             input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("TRANSPARENCY", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))


class Text2Speech:
    class SpeakAndWait(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "text2speech_speakAndWait", _shadow=shadow, pos=pos)

        def set_words(self, value: str = "50", input_type: str | int = "number", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("WORDS", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class SetVoice(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "text2speech_setVoice", _shadow=shadow, pos=pos)

        def set_voice(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("VOICE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class MenuVoices(Block):
        def __init__(self, *, shadow: bool = True, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "text2speech_menu_voices", _shadow=shadow, pos=pos)

        def set_voices(self, value: str = "ALTO", value_id: Optional[str] = None):
            return self.add_field(Field("voices", value, value_id))

    class SetLanguage(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "text2speech_setLanguage", _shadow=shadow, pos=pos)

        def set_language(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                         input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("LANGUAGE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class MenuLanguages(Block):
        def __init__(self, *, shadow: bool = True, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "text2speech_menu_languages", _shadow=shadow, pos=pos)

        def set_languages(self, value: str = "en", value_id: Optional[str] = None):
            return self.add_field(Field("languages", value, value_id))


class Translate:
    class GetTranslate(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "translate_getTranslate", _shadow=shadow, pos=pos)

        def set_words(self, value="hello!", input_type: str | int = "string", shadow_status: int = 1, *,
                      input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("WORDS", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

        def set_language(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                         input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("LANGUAGE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class MenuLanguages(Block):
        def __init__(self, *, shadow: bool = True, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "translate_menu_languages", _shadow=shadow, pos=pos)

        def set_languages(self, value: str = "sv", value_id: Optional[str] = None):
            return self.add_field(Field("languages", value, value_id))

    class GetViewerLanguage(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "translate_getViewerLanguage", _shadow=shadow, pos=pos)


class MakeyMakey:
    class WhenMakeyKeyPressed(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "makeymakey_whenMakeyKeyPressed", _shadow=shadow, pos=pos)

        def set_key(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                    input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("KEY", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class MenuKey(Block):
        def __init__(self, *, shadow: bool = True, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "makeymakey_menu_KEY", _shadow=shadow, pos=pos)

        def set_key(self, value: str = "SPACE", value_id: Optional[str] = None):
            return self.add_field(Field("KEY", value, value_id))

    class WhenCodePressed(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "makeymakey_whenCodePressed", _shadow=shadow, pos=pos)

        def set_sequence(self, value, input_type: str | int = "block", shadow_status: int = 1, *,
                         input_id: Optional[str] = None, obscurer: Optional[str | Block] = None):

            if isinstance(value, Block):
                value = self.target.add_block(value)
            elif isinstance(value, list) or isinstance(value, tuple):
                if isinstance(value[0], Block):
                    value = self.target.link_chain(value)
            return self.add_input(
                Input("SEQUENCE", value, input_type, shadow_status, input_id=input_id, obscurer=obscurer))

    class MenuSequence(Block):
        def __init__(self, *, shadow: bool = True, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "makeymakey_menu_SEQUENCE", _shadow=shadow, pos=pos)

        def set_key(self, value: str = "LEFT UP RIGHT", value_id: Optional[str] = None):
            return self.add_field(Field("SEQUENCE", value, value_id))


class CoreExample:
    class ExampleOpcode(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "coreExample_exampleOpcode", _shadow=shadow, pos=pos)

    class ExampleWithInlineImage(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "coreExample_exampleWithInlineImage", _shadow=shadow, pos=pos)


class OtherBlocks:
    class Note(Block):
        def __init__(self, *, shadow: bool = True, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "note", _shadow=shadow, pos=pos)

        def set_note(self, value: str = "60", value_id: Optional[str] = None):
            return self.add_field(Field("NOTE", value, value_id))

    class Matrix(Block):
        def __init__(self, *, shadow: bool = True, pos: tuple[int | float, int | float] = (0, 0)):
            super().__init__(None, "matrix", _shadow=shadow, pos=pos)

        def set_note(self, value: str = "0101010101100010101000100", value_id: Optional[str] = None):
            return self.add_field(Field("MATRIX", value, value_id))

    class RedHatBlock(Block):
        def __init__(self, *, shadow: bool = False, pos: tuple[int | float, int | float] = (0, 0)):
            # Note: There is no single opcode for the red hat block as the block is simply the result of an error
            # The opcode here has been set to 'redhatblock' to make it obvious what is going on

            # (It's not called red_hat_block because then TurboWarp thinks that it's supposed to find an extension
            # called red)

            # Appendix: You **CAN** actually add comments to this block, however it will make the block misbehave in the
            # editor. The link between the comment and the block will not be visible, but will be visible with the
            # corresponding TurboWarp addon
            super().__init__(None, "redhatblock", _shadow=shadow, pos=pos, can_next=False)
