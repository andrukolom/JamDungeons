from main.models import Usual_tags, Tags_Connect


class Tags_checkout:
    def __init__(self, tag) -> None:
        self.__tag = tag
        self.__tag_id = Usual_tags.objects.get(tag=self.__tag).id

    def popular_tag(self) -> bool:
        count_tag: int = Tags_Connect.objects.filter(tag_id=self.__tag_id).count()
        if count_tag >= 25:
            return True
        return False

    def can_write_tag(self):
        if self.popular_tag():
            return True
        return False
