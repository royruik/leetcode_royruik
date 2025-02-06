// Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.

// An input string is valid if:

// Open brackets must be closed by the same type of brackets.
// Open brackets must be closed in the correct order.
// Every close bracket has a corresponding open bracket of the same type.
 

// Example 1:

// Input: s = "()"

// Output: true

// Example 2:

// Input: s = "()[]{}"

// Output: true

// Example 3:

// Input: s = "(]"

// Output: false

// Example 4:

// Input: s = "([])"

// Output: true

// HINT:
// Use a stack of characters.
// When you encounter an opening bracket, push it to the top of the stack.
// When you encounter a closing bracket, check if the top of the stack was the opening for it. If yes, pop it from the stack. Otherwise, return false.
class Solution {
    public char itsopening(char c){
        if(c == ')'){
            return '(';
        }
        else if(c == ']'){
            return '[';
        }
        else if(c == '}'){
            return '{';
        }
        return ' ';
    }
    public boolean isValid(String s) {
        Stack<Character> stack = new Stack<>();
        for (int i = 0; i < s.length() ;i++ ) {
            //or "([{".indexOf(s.charAt(i)) != -1
            if (s.charAt(i) == '(' || s.charAt(i) == '[' || s.charAt(i) == '{') {
                stack.push(s.charAt(i));
                continue;
            }
            if (s.charAt(i) == ')' || s.charAt(i) == ']' || s.charAt(i) == '}') {
                if (stack.size() == 0) {
                    return false;
                }
                if (stack.peek() != itsopening(s.charAt(i))) {
                    return false;
                }
                stack.pop();
            }
        }
        if (stack.size() == 0) {
            return true;
        }
        return false;
    }
}