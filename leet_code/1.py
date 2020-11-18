from typing import List

class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        cache = {}

        for i, v in enumerate(nums):
            rem = target - v
            if rem in cache:
                return i, cache[rem]
            else:
                cache[v] = i


solution = Solution()
r1 = solution.twoSum(nums=[2,7,11,15], target=9)
print(r1)


