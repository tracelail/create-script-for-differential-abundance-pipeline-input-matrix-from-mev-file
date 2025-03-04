import pandas as pd
import numpy as np

class MevToCsv:
    def __init__(self, mev_path, csv_path):
        self.mev_path = mev_path
        self.csv_path = csv_path
        self.dataframe = None

    @property
    def sample_identifier(self) -> str:
        sample_identifier = self.mev_path.split('/')[-1].split('.')[0]
        return sample_identifier
    
    @classmethod
    def read_mev_header(cls, mev_path):
        with open(mev_path, 'r') as f:
            mev_header = {}
            for i in range(7):
                line = f.readline().replace('#','').strip()
                key, value = line.split(':',1)
                mev_header[key] = value.strip()
        return mev_header
    
    @classmethod
    def read_mev_data(cls, mev_path, skiprows=8):
        ## read the data from the file
        # skiprows=8 to skip the header ## potential that all mev files have the same header number of rows
        df = pd.read_csv(mev_path, sep='\t', skiprows=skiprows)
        return df
    
    def create_expression_matrix(self, dataframe):
        ## create the expression matrix
        # calculate expression value from IA and IB values
        # expression = np.log2(IA/IB)
        # Gene identifier in mev file is the 'FeatName' column
        expression_matrix = dataframe.copy()
        expression_matrix['log2_expression'] = np.log2(expression_matrix['IA']/expression_matrix['IB'])
        expression_matrix = expression_matrix[['FeatName','log2_expression']]
        return expression_matrix
    
    
    
    
    
    def convert(self):
        mev_header = self.read_mev_header(self.mev_path)
        df = self.read_mev_data(self.mev_path)
        expression_matrix = self.create_expression_matrix(df)
        expression_matrix.to_csv(self.csv_path, index=False)
        return mev_header, expression_matrix