from pathlib import Path
import pandas as pd
import shapely as shp
import figs as f

class BaseData:

    def __init__(self):

        self.name = None


class ExcelData(BaseData):

    def __init__(
            self,
            excel_paths: Path | list = None,

    ):
        """
        Class to import data from excel files into Pandas DataFrames
        :param excel_paths: Paths to excel files, can give a single Path or a list of Paths
        """
        super().__init__()

        self._excel_dict = None
        self._excel_paths = None
        self.excel_paths = excel_paths

    @property
    def excel_dict(self):
        if self._excel_dict is None:
            self._excel_dict = {}
            for excel_path in self.excel_paths:
                self.add_excel(excel_path)
        return self._excel_dict

    @excel_dict.setter
    def excel_dict(self, val):
        if self._excel_dict is None:
            self._excel_dict = {}
        if val is not None:
            assert isinstance(val, dict), 'excel_dict must be dict'
        self._excel_dict = val

    @property
    def excel_paths(self):
        return self._excel_paths

    @excel_paths.setter
    def excel_paths(self, val):
        if val is None:
            self._excel_paths = []
        if isinstance(val, list):
            for item in list:
                assert isinstance(item, Path), 'excel paths provided must be Path objects'
        elif isinstance(val, Path):
            val = [val]
        else:
            raise TypeError('excel_paths must be a list or a Path object')
        self._excel_paths = val

    def add_excel(self, excel_path: Path):
        """Method to add a DataFrame from an excel file Path object to the excel_dict"""
        assert isinstance(excel_path, Path), 'excel_path must be a Path object'
        try:
            pd_excel = pd.read_excel(excel_path)
        except ValueError:
            print(f"can't read excel file: {excel_path}")
        self.excel_dict.update({excel_path.name: {
            'Path': excel_path,
            'DataFrame': pd_excel}
        })

    def get_idx(self, idx=None):
        """Method to get a DataFrame of an excel file based on its index in the excel_dict"""
        idx = 0 if idx is None else idx
        assert isinstance(idx, int), 'idx must be int'
        key = list(self.excel_dict.keys())[idx]
        return self.excel_dict[key]['DataFrame']

    @property
    def dfs(self):
        """Method to get a list of all DataFrames in excel_dict"""
        return [self.get_idx(idx) for idx in range(len(self.excel_dict))]


class ExcelDateData(ExcelData):
    def __init__(
            self,
            excel_paths: Path | list = None,
            date_label: str = 'date',
            auto_date_to_index: bool = True
    ):
        super().__init__(excel_paths=excel_paths)
        self.date_label = date_label
        self.auto_date_to_index = auto_date_to_index

        if self.auto_date_to_index:
            self.set_date_to_index()

    def set_date_to_index(self, date_label: str = None):
        """sets the first column with date_label.lower in the name to the DataFrame index"""
        date_label = self.date_label if date_label is None else date_label
        for name, excel in self.excel_dict.items():
            df = excel['DataFrame']
            for col in list(df.columns):
                if self.date_label in str.lower(col):
                    df.set_index(col, inplace=True)
                    return

    def plot(self, idx=0):
        """Method to plot a DataFrame based on its index in the excel_dict"""
        df = self.get_idx(idx)
        fig = f.Fig()
        for col in df.columns:
            fig.add_scattergl(x=df.index, y=df[col], name=col)
        return fig.show()
