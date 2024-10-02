// You are given an integer array nums. You are initially positioned at the array's first index, and each element in the array represents your maximum jump length at that position.

// Return true if you can reach the last index, or false otherwise.

 

// Example 1:

// Input: nums = [2,3,1,1,4]
// Output: true
// Explanation: Jump 1 step from index 0 to 1, then 3 steps to the last index.
// Example 2:

// Input: nums = [3,2,1,0,4]
// Output: false
// Explanation: You will always arrive at index 3 no matter what. Its maximum jump length is 0, which makes it impossible to reach the last index.
 

// Constraints:

// 1 <= nums.length <= 104
// 0 <= nums[i] <= 105

// Thought: Maybe check every 0's? (brutal solution)
// recursive help function? (...)
class Solution {
    public boolean canJump(int[] nums) {
        if(nums.length < 2){ //The ending point is the starting point.
            return true;
        }
    	for (int i = 0; i < nums.length - 1; i++) { //Loop over the array (except the ending point) to find the breakpoints (0's)
    		if (nums[i] == 0) { //We found it!
    			int j = 0;
    			boolean flag = false;  //flag = false: keep the while loop (as now we didnt find the solution to jump the breakpoint)
    			while(j < i && !flag){ //Only the element before the breakpoint is checked
    				if (j + nums[j] > i) {//When certain point's value can exceed the breakpoint
    					flag = true;//flag = true: we find the solution, this breakpoint can be ignored
    				}
                    j++;//loop over the possible points
    			}
    			if (flag == false) {//after the iteration, we dont find the solution
    				return false;//as such, the mission failed
    			}

    		}
    	}
    	return true;//we found the solution for every breakpoints we detected, mission accomplished
    }
}