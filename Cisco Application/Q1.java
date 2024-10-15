
import java.util.*;
import java.lang.*;
import java.io.*;

/*
 * grid, represents the letters in the grid of size N*M.
word, represents the words to be searched of size K.
 */
public class Solution
{
	public static void  funcPuzzle(char[][] grid, String[] word)
	{
		// Write your code here
		StringBuilder result = new StringBuilder();
		int rows = grid.length;
		int cols = grid[0].length;
		List<String> dictionary = new ArrayList<>();


		for (int i = 0; i < rows; i++){
			String rowString = new String(grid[i]);
			String reversedRowString = new StringBuilder(rowString).reverse().toString();
			dictionary.add(rowString);
			dictionary.add(reversedRowString);
		}
		for (int j = 0; j < cols; j++){
			StringBuilder colString = new StringBuilder();
				for(int i = 0; i < rows; i++){
					colString.append(grid[i][j]);
				}
			String colStr = colString.toString();
			String reversedColString = colString.reverse().toString();
			dictionary.add(colStr);
			dictionary.add(reversedColString);
		}
		for (int i = 0; i < word.length; i++){
			if(dictionary.contains(word[i])){
				result.append("Yes ");
			}
			else{
				result.append("No ");
			}
		}
		System.out.println(result.toString().trim());
		
	}

	public static void main(String[] args)
	{
		Scanner in = new Scanner(System.in);
		// input for grid
		int grid_row = in.nextInt();
		int grid_col = in.nextInt();
		char grid[][] = new char[grid_row][grid_col];
		for(int idx = 0; idx < grid_row; idx++)
		{
			for(int jdx = 0; jdx < grid_col; jdx++)
			{
				grid[idx][jdx] = in.next().charAt(0);
			}
		}
		//input for word
		int word_size = in.nextInt();
		String word[] = new String[word_size];
		for(int idx = 0; idx < word_size; idx++)
		{
			word[idx] = in.next();
		}
		
		
		funcPuzzle(grid, word);
	}
}