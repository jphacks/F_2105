import inspect
from datetime import datetime


# reprなどの共通要素をクラスにした
class Expression(object):

    def __init__(self, *args, **kwargs):

        sig = inspect.signature(self.__init__)

        # 型チェック
        for k, v in sig.bind(*args, **kwargs).arguments.items():
            annot = sig.parameters[k].annotation
            t = annot if isinstance(annot, type) else inspect._empty
            if t is not inspect._empty and not isinstance(v, t):
                raise TypeError('{k} must be {tname} not, {vcls_name}.'.format(
                        k        =k,
                        tname    =t.__name__,
                        vcls_name=v.__class__.__name__
                    ))

            self.__dict__[k] = v

        self.timestamp = datetime.strftime(datetime.now(), '%y-%m-%d %H:%M:%S')


    @classmethod
    def from_dict(cls, q):

        return cls(**q)


    def to_dict(self):

        return self.__dict__


    def __setattr__(self, k, v):

        if k not in self.__dict__ or type(v) == type(self.__dict__[k]):
            self.__dict__[k] = v

        else:
            raise TypeError('{k} muse be {tname}, not {vcls_name}'.format(
                   k        =k,
                   tname    =self.__dict__[k].__class__.__name__,
                   vcls_name=v.__class__.__name__
                ))


    def __repr__(self):

        return '{cls_name}({vals})'.format(
                cls_name=self.__class__.__name__,
                vals    =', '.join(f'{k}={v}' for k, v in self.__dict__.items())
            )



# ニュース
class News(Expression):

    def __init__(self,
            title: str, news_id: str, url: str, imgsrc: str
        ):

        super().__init__(title, news_id, url, imgsrc)



# 参加者登録
class Room(Expression):

    def __init__(self,
            name: str, zoom_id: str
        ):

        super().__init__(name, zoom_id)



# 参加者発言
class Speech(Expression):

    def __init__(self,
            name: str, zoom_id: str, text: str
        ):

        super().__init__(name, zoom_id, text)



# 参加者興味
class Interest(Expression):

    def __init__(self,
            name: str, news_id: str, degree: int
        ):

        if not 0 < degree <= 10:
            raise ValueError(f'degree must be in (0, 10]. <{degree=}>')

        super().__init__(name, news_id, degree)



class Evaluation(Expression):

    def __init__(self,
            name: str, zoom_id: str,
            angry: int, disgust: int, fear: int, happy: int,
            sad: int, surprise: int, neutral: int,
            speaking_im_b64: str
        ):

        super().__init__(
                name, zoom_id,
                angry, disgust, fear, happy,
                sad, surprise, neutral,
                speaking_im_b64)
