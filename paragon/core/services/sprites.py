import logging
from typing import Optional, Tuple

from PySide2.QtGui import QPixmap
from PySide2.QtCore import QTimer, QDateTime
from paragon.ui.controllers.sprites import SpriteItem

class Sprites:
    def __init__(self, gd):
        self.gd = gd

        self.defaults = {
            "緑": QPixmap("resources/misc/allied.png"),
            "赤": QPixmap("resources/misc/enemy.png"),
            "青": QPixmap("resources/misc/player.png"),
        }
        self.team_names = ["青", "赤", "緑"]

        self.timer = QTimer()
        self.sprite_items = list()
        self.activated = list()
        self.timer.timeout.connect(self._next_frame)

        # A test for now
        self.timer.start(1000/30)

    def add_sprite_to_handler(self, sprite_item: SpriteItem):
        if self.timer.isActive():
            self.activated.append(QDateTime().currentMSecsSinceEpoch())
        sprite_item.handler = self
        self.sprite_items.append(sprite_item)

    def delete_sprite_from_handler(self, sprite_item: SpriteItem):
        for item in self.sprite_items:
            if item == sprite_item:
                self.sprite_items.remove(sprite_item)

    def start_handler(self):
        time = QDateTime().currentMSecsSinceEpoch()
        self.activated = [time for _ in range(len(self.sprite_items))]
        # Check every 30Hz or 30FPS for layman's terms
        self.timer.start(1000/30)
    
    def stop_handler(self):
        self.timer.stop()

    def _next_frame(self):
        current_time = QDateTime().currentMSecsSinceEpoch()
        for x in range(len(self.sprite_items)):
            # If sprite is loaded
            if sprite := self.sprite_items[x].sprite:
                # If the sprite has animation data
                if animation_data := sprite.animation_data:
                    if (current_time - self.activated[x])/sprite.animation_data[self.sprite_items[x].animation_index].frame_data[self.sprite_items[x].frame_index].frame_delay > 1:
                        self.activated[x] = current_time
                        
                        # Fire signal here
                        self.sprite_items[x].next_frame()

    # Need to fix return type
    def from_spawn(self, spawn, person_key=None) -> Optional[QPixmap]:
        team = 0
        try:
            team = self.gd.int(spawn, "team")
            pid = self.gd.string(spawn, "pid")
            job, fallback = self._get_jobs(pid, person_key)
            if not job:
                return self.default(team)
            else:
                pid = pid[4:] if pid and pid.startswith("PID_") else pid
                job = job[4:] if job.startswith("JID_") else job
                fallback = (
                    fallback[4:]
                    if fallback and fallback.startswith("JID_")
                    else fallback
                )
                return self.load(pid, job, team, fallback_job=fallback)
        except:
            logging.exception("Failed to read sprite from spawn.")
            return self.default(team)

    # Need to fix return type
    def load(self, char, job, team, fallback_job=None) -> Optional[QPixmap]:
        try:
            team_name = self.team_name(team)
            if team_name:
                if sprite := self._load(
                    char, job, team_name, fallback_job=fallback_job
                ):
                    return sprite
                else:
                    return self.default(team)
        except:
            logging.exception(
                f"Failed to load sprite char={char}, job={job}, team={team}"
            )
            return self.default(team)

        # Need to fix return type
    def default(self, team: int) -> Optional[QPixmap]:
        team_name = self.team_name(team)
        return self._default(self.defaults[team_name], team_name) if team_name in self.defaults else None

    def _get_jobs(self, pid, person_key=None) -> Tuple[Optional[str], Optional[str]]:
        job = None
        fallback = None
        if person_key:
            job, fallback = self._person_to_jobs(pid, person_key)
        if not job:
            job, fallback = self._static_character_to_jobs(pid)
        return job, fallback

    def _person_to_jobs(self, pid, person_key) -> Tuple[Optional[str], Optional[str]]:
        raise NotImplementedError

    def _static_character_to_jobs(self, pid) -> Tuple[Optional[str], Optional[str]]:
        raise NotImplementedError

    def _load(self, char, job, team, fallback_job=None) -> Optional[QPixmap]:
        raise NotImplementedError

    # Need to fix return type 
    def _default(self, spritesheet: QPixmap):
        raise NotImplementedError

    def team_name(self, team_number: int) -> Optional[str]:
        if team_number in range(0, len(self.defaults)):
            return self.team_names[team_number]
        else:
            return None