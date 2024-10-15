
import java.util.*;
import java.lang.*;
import java.io.*;

/*
 * matrix, represents the elements of the matrix of size N*M.
 */
public class Solution
{
	
	public static void  funcMatrix(int[][] matrix)
	{
		// Write your code here
		int rows = matrix.length;
		int cols = matrix[0].length;
		for(int i = 0;i< rows; i++){
			int maxInRow = matrix[i][0];
			int colIndex = 0;
			for(int j = 1; j < cols; j++){
				if(matrix[i][j] > maxInRow){
					maxInRow = matrix[i][j];
					colIndex = j;
				}
			}
			boolean smallest = true;
			for(int k = 0; k < rows; k++){
				if(matrix[k][colIndex] < maxInRow){
					smallest = false;
					break;
				}
			}
			if(smallest){
				System.out.println(maxInRow);
				return;
			}
		}
		System.out.println(-1);


		
	}

	public static void main(String[] args)
	{
		Scanner in = new Scanner(System.in);
		// input for matrix
		int matrix_row = in.nextInt();
		int matrix_col = in.nextInt();
		int matrix[][] = new int[matrix_row][matrix_col];
		for(int idx = 0; idx < matrix_row; idx++)
		{
			for(int jdx = 0; jdx < matrix_col; jdx++)
			{
				matrix[idx][jdx] = in.nextInt();
			}
		}
		
		
		funcMatrix(matrix);
	}
}