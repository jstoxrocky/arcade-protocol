import os
_inner_file = os.path.dirname(__file__)
_outer_dir_rel = os.path.join(_inner_file, '..')
_outer_dir_abs = os.path.abspath(_outer_dir_rel)
CONTRACTS_DIR = os.path.join(_outer_dir_abs, 'contracts')
