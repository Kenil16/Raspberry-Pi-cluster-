import sys
import os
from mpi4py import MPI
from big_data_processing  import*

instance = data_processing()

#Init OpencvMPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
p = comm.Get_size()

#Get number of blocks 
instance.read_blocks_from_file("output/blocks.txt")
n = len(instance.list_of_blocks)

#Get number of local blocks to calculate 
local_n = n/p

#Find interval for each process based on rank
interval = []
interval.append(rank*local_n)

if rank == (p-1):
    interval.append(rank*local_n + local_n + (n - rank*local_n - local_n))
else:
    interval.append(rank*local_n + local_n)

#Find pumpkins
test_images = ['../input/test_image_pumpkin3.png', '../input/test_image_pumpkin4.png']
instance.partition_blocks(interval)
pumpkins = instance.process_blocks("../input/orthomosaic1.tif",test_images,"lab",1,4.5)

total_pumpkins = comm.reduce(pumpkins)

#Print final result 
if rank == 0:
    print("Total number of pumpkins found: " + str(total_pumpkins))

MPI.Finalize
