from math import log2
from random import randrange
from matplotlib import pyplot as plt


class DataPlot:

    def __init__(self, fig, axs, figtitle, result_list, blk_size, mway):
        self.fig = fig
        self.axs = axs
        self.blk_size = blk_size
        self.mway = mway
        self.result_list = result_list
        self.figtitle = figtitle

    def plot(self):

        self.fig.suptitle(self.figtitle)

        self.axs[0, 0].plot(self.blk_size, self.result_list["16384"][f"{self.mway}"])
        self.axs[0, 0].set_title("16KB")
        self.axs[0, 0].set_xlabel("Block_Size")
        self.axs[0, 0].set_ylabel("Hit %")

        self.axs[0, 1].plot(self.blk_size, self.result_list["32768"][f"{self.mway}"])
        self.axs[0, 1].set_title("32KB")
        self.axs[0, 1].set_xlabel("Block_Size")
        self.axs[0, 1].set_ylabel("Hit %")

        self.axs[1, 0].plot(self.blk_size, self.result_list["65536"][f"{self.mway}"])
        self.axs[1, 0].set_title("64KB")
        self.axs[1, 0].set_xlabel("Block_Size")
        self.axs[1, 0].set_ylabel("Hit %")

        self.axs[1, 1].plot(self.blk_size, self.result_list["131072"][f"{self.mway}"])
        self.axs[1, 1].set_title("128KB")
        self.axs[1, 1].set_xlabel("Block_Size")
        self.axs[1, 1].set_ylabel("Hit %")

        plt.show()


class CacheMem:
    mem = {}
    hit = 0
    miss = 0
    total = 0
    hit_per = 0

    def __init__(self, size, block_size, m_way, rep_policy):
        self.address = 0
        self.debug = False
        self.size = size
        self.block_size = block_size
        self.m_way = m_way
        self.rep_policy = rep_policy
        self.num_block = size / block_size

    def reset(self):
        self.mem.clear()
        self.address = 0
        self.hit = 0
        self.miss = 0
        self.total = 0
        self.hit_per = 0

    def set_debug(self, debug):
        self.debug = bool(debug)

    def print(self):
        print(f"************************************")
        print(f"  **** CACHE MEMORY ****")
        print(f"    Size       = {self.size}")
        print(f"    Block_Size = {self.block_size}")
        print(f"    M_Ways     = {self.m_way}")
        print(f"    Policy     = {self.rep_policy}")
        print(f"    Num_Blocks = {int(self.num_block)}")

    def result(self):
        self.total = self.hit + self.miss
        self.hit_per = (self.hit * 100) / self.total
        self.print()
        print(f"    # HITS : {self.hit}")
        print(f"    # Miss : {self.miss}")
        print(f"    # Total : {self.total}")
        print(f"    Hit % : {self.hit_per}")
        print(f"************************************")

    def access(self, address):
        if self.debug == 1:
            self.address = address
        else:
            self.address += address

        mem_block = int(self.address / self.block_size)
        cache_set = int(mem_block % self.num_block)

        # Check if Block exist in Cache
        if f"{cache_set}" in self.mem:
            if self.mem[f"{cache_set}"].count(mem_block) != 0:
                self.hit += 1
                if self.rep_policy == "LRU":
                    self.mem[f"{cache_set}"].remove(mem_block)
                    self.mem[f"{cache_set}"].append(mem_block)
            else:
                # If num of block cached < m_ways, add block
                if len(self.mem[f"{cache_set}"]) < self.m_way:
                    self.miss += 1
                    self.mem[f"{cache_set}"].append(mem_block)
                else:
                    self.miss += 1
                    if self.rep_policy == "Random":
                        index = randrange(self.m_way)
                        self.mem[f"{cache_set}"].pop(index)
                        self.mem[f"{cache_set}"].append(mem_block)
                    else:  # FIFO/LRU
                        self.mem[f"{cache_set}"].pop(0)
                        self.mem[f"{cache_set}"].append(mem_block)

        else:
            self.miss += 1
            self.mem[f"{cache_set}"] = [mem_block]
            sorted_keys = sorted(self.mem.keys())
            self.mem = {key: self.mem[key] for key in sorted_keys}

        if self.debug is True:
            print(f"Address : {address} | Absolute Address : {self.address}  | Memory_Block : {mem_block} | Cache "
                  f"Block : {cache_set}")


debug = 0
regression = 1
Cache_Size = 16 * 1024
Block_Size = 32
Set_Way = 1
Replacement_Policy = "FIFO"
result = dict()

if regression == 0:
    CM = CacheMem(Cache_Size, Block_Size, Set_Way, Replacement_Policy)
    CM.set_debug(debug)
    with open("/Users/dachariy_sjsu/Downloads/addr_trace.txt", "r") as fp:
        count = 0
        while True:
            line = fp.readline()
            line.strip()
            count += 1

            if not line:
                break
            CM.access(int(line))

    CM.result()
else:
    Cache_Size = [16 * 1024, 32 * 1024, 64 * 1024, 128 * 1024]
    Block_Size = [32, 64, 128, 256]
    Set_Way = [1, 2, 4, 8, 16]

    # Cache_Size = [16 * 1024]
    # Block_Size = [32]
    # Set_Way = [1]

    # Use Replacement_Policy one by one manually
    # Replacement_Policy = ["FIFO", "LRU", "Random"]
    Replacement_Policy = ["FIFO"]

    for RP in Replacement_Policy:
        for CS in Cache_Size:
            result[f"{CS}"] = dict()
            for SW in Set_Way:
                result[f"{CS}"][f"{SW}"] = list()
                for BS in Block_Size:
                    CM = CacheMem(CS, BS, SW, RP)
                    CM.set_debug(debug)
                    with open("/Users/dachariy_sjsu/Downloads/addr_trace.txt", "r") as fp:
                        count = 0
                        while True:
                            line = fp.readline()
                            line.strip()
                            count += 1

                            if not line:
                                break
                            CM.access(int(line))
                    CM.result()
                    result[f"{CS}"][f"{SW}"].append(round(CM.hit_per, 4))

print(result)
fig, axs = plt.subplots(2, 2)
DP_0 = DataPlot(fig, axs, "FIFO - Way:1", result, Block_Size, 1)
DP_0.plot()

fig1, axs1 = plt.subplots(2, 2)
DP_1 = DataPlot(fig1, axs1, "FIFO - Way:2", result, Block_Size, 2)
DP_1.plot()

fig2, axs2 = plt.subplots(2, 2)
DP_2 = DataPlot(fig2, axs2, "FIFO - Way:4", result, Block_Size, 4)
DP_2.plot()

fig3, axs3 = plt.subplots(2, 2)
DP_3 = DataPlot(fig3, axs3, "FIFO - Way:8", result, Block_Size, 8)
DP_3.plot()

fig4, axs4 = plt.subplots(2, 2)
DP_4 = DataPlot(fig4, axs4, "FIFO - Way:16", result, Block_Size, 16)
DP_4.plot()
