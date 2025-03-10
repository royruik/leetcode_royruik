// Given an integer array nums, rotate the array to the right by k steps, where k is non-negative.

 

// Example 1:

// Input: nums = [1,2,3,4,5,6,7], k = 3
// Output: [5,6,7,1,2,3,4]
// Explanation:
// rotate 1 steps to the right: [7,1,2,3,4,5,6]
// rotate 2 steps to the right: [6,7,1,2,3,4,5]
// rotate 3 steps to the right: [5,6,7,1,2,3,4]
// Example 2:

// Input: nums = [-1,-100,3,99], k = 2
// Output: [3,99,-1,-100]
// Explanation: 
// rotate 1 steps to the right: [99,-1,-100,3]
// rotate 2 steps to the right: [3,99,-1,-100]
 

// Constraints:

// 1 <= nums.length <= 105
// -231 <= nums[i] <= 231 - 1
// 0 <= k <= 105
 

// Follow up:

// Try to come up with as many solutions as you can. There are at least three different ways to solve this problem.
// Could you do it in-place with O(1) extra space?

//************************************************************************************************
// Original Solution: (Will not pass the larger data test, get called "Naive Approach Using Cyclic Swaps" by ChatGPT)
// class Solution {
//     public void rotate(int[] nums, int k) {
//     	while(k > 0){
//     		int temp;
//     		for (int i = 0; i < nums.length ; i++ ) {
//     			temp = nums[i];
//     			nums[i] = nums[nums.length - 1];
//     			nums[nums.length - 1] = temp;
//     		}
//     		k--;
//     	}
//     }
// }
class Solution {
    public void rotate(int[] nums, int k) {
        k %= nums.length;
        reverse(nums, 0, nums.length - 1);
        reverse(nums, 0, k - 1);
        reverse(nums, k, nums.length - 1);
    }

    public void reverse(int[] nums, int start, int end) {
        while (start < end) {
            int temp = nums[start];
            nums[start] = nums[end];
            nums[end] = temp;
            start += 1;
            end -= 1;
        }
    }
}
// 原始数组	1 2 3 4 5 6 7
// 翻转所有元素	7 6 5 4 3 2 1
// 翻转 [0,k mod n−1] 区间的元素	5 6 7 4 3 2 1
// 翻转 [k mod n,n−1] 区间的元素	5 6 7 1 2 3 4

]