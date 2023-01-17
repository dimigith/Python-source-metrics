import abc

import pandas as pd

from src.utils.file_strategies import DataframeFile, HTMLFile
from src.utils.logs import log_green, log_obj_stage


class SingletonClass(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingletonClass, cls).__new__(cls, *args, **kwargs)
        else:
            log_green(f"(CACHED) Object {cls.__name__} is already initialized.")
        return cls.instance


class AbstractObject(SingletonClass, abc.ABC):
    def __init__(self, file_strategy=None):
        self._file_strategy = file_strategy
        self._data = None

    def data(self):
        # try:
        return self._prepare_data()
        # except Exception as e:
        #     log_red(str(e))
        #     return f"{self.__class__.__name__}: {e}"

    def _prepare_data(self):
        if self._data is not None:  # if self._data breaks in Dataframes
            return self._data

        if self._file_strategy:
            self._data = self._file_strategy.load()

        if self._data is None:
            log_obj_stage(f"{self.__class__.__name__} object is building.")
            self._data = self.build()
            log_obj_stage(f"{self.__class__.__name__} object finished.")

            if self._file_strategy and self._data is not None:# if self._data breaks in Dataframes
                self._file_strategy.save(self._data)

        return self._data

    @abc.abstractmethod
    def build(self):
        return None


class DataframeObject(AbstractObject, abc.ABC):
    def __init__(self, read_csv_kwargs=None, to_csv_kwargs=None):
        super().__init__(DataframeFile(self,
                                       save_kwargs=to_csv_kwargs,
                                       load_kwargs=read_csv_kwargs))

    @property
    def dataframe(self):
        build_res = self.build()
        if not isinstance(build_res, pd.DataFrame) and not isinstance(build_res, pd.Series):
            raise TypeError(f"Wrong return type: build method of DataframeObject objects must return pandas.DataFrame or pandas.Series. got {type(build_res)}")
        return build_res


class HTMLObject(AbstractObject, abc.ABC):
    def __init__(self):
        super().__init__(HTMLFile(self))

    @property
    def html(self):
        build_res = self.build()
        if not isinstance(build_res, str):
            raise TypeError(f"Wrong return type: build method of HTMLObject objects must return string. got {type(build_res)}")
        return build_res


class HTMLTableObject(HTMLObject, abc.ABC):
    def __init__(self):
        super().__init__()

    def title(self):
        def _space_before_upper_case(s):
            return ''.join([(f" {c}" if c.isupper() else c) for c in s])
        return _space_before_upper_case(self.__class__.__name__)

    @abc.abstractmethod
    def build_dataframe(self):
        pass

    def build(self):
        build_res = self.build_dataframe()
        if not isinstance(build_res, pd.DataFrame):
            raise TypeError(
                f"Wrong return type: build_dataframe method of HTMLTableObject objects must return pandas.DataFrame. got {type(build_res)}")

        # html_table_str = SimpleHTMLTable(build_res).html
        # return html_table_str
        title = self.title() if self.title() else ''
        table_html = build_res.to_html(index=False, justify='center')
        return f"<h3>{title}</h3>{table_html}<br>"