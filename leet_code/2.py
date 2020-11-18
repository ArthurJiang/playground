# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def addTwoNumbers(self, l1: ListNode, l2: ListNode) -> ListNode:
        res = ListNode()
        cur_node = res 
        tmp_sum = 0
        rem = 0
        
        while l1 != None or l2 != None or rem != 0:
            if l1 != None:
                tmp_sum += l1.val
                l1 = l1.next
            if l2 != None:
                tmp_sum += l2.val
                l2 = l2.next
               
            tmp_sum += rem
            
            if tmp_sum >= 10:
                cur_digit = tmp_sum - 10
                rem = 1
            else:
                cur_digit = tmp_sum
                rem = 0

            cur_node.val = cur_digit
            tmp_sum = 0

            if l1 != None or l2 != None or rem != 0:        
                cur_node.next = ListNode()
                cur_node = cur_node.next
            
        return res

l1_arr = [2,4,3]
l2_arr = [5,6,4]

def array2linked_list(arr):
    l = ListNode()
    cur_l = l
    for i, v in enumerate(arr):
        cur_l.val = v
        if i != len(arr) - 1:
            cur_l.next = ListNode()
            cur_l = cur_l.next
    return l

l1 = array2linked_list(l1_arr)
l2 = array2linked_list(l2_arr)

def linked_list2array(ll):
    res = []
    while ll != None:
        res.append(ll.val)
        ll = ll.next
    return res

solution = Solution()
so_res = linked_list2array(solution.addTwoNumbers(l1=l1, l2=l2))
print(so_res)