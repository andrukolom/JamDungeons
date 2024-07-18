from main.models import Quest, Hashtag

class Tags_checkout:
    def __init__(self, tag) -> None:
        self.__tag = tag
    def popular_tag(self) -> bool:
        count_tag: int = len(Quest.objects.filter(tag=self.__tag))
        if count_tag >= 20:
            return True
        return False
    def tag_already_exist(self) -> bool:
        does_tag_exist: int = len(Hashtag.objects.filter(tag=self.__tag))
        if(does_tag_exist >= 1):
            return True
        return False

    def can_write_tag(self):
        if (self.popular_tag() and not self.tag_already_exist()):
            return True
        return False
