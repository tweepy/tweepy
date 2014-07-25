 /**
 * --Copyright notice-- 
 *
 * Copyright (c) School of Geography, University of Leeds. 
 * http://www.geog.leeds.ac.uk/
 * This software is licensed under 'The Artistic License' which can be found at 
 * the Open Source Initiative website at... 
 * http://www.opensource.org/licenses/artistic-license.php
 * Please note that the optional Clause 8 does not apply to this code.
 *
 * The Standard Version source code, and associated documentation can be found at... 
 * [online] http://mass.leeds.ac.uk/
 * 
 *
 * --End of Copyright notice-- 
 *
 */
 
import java.io.*;
import java.util.*;
import java.awt.*;
import java.nio.charset.Charset;

 
/**
* Reads and writes file data.
* @version 1.0
* @author <A href="http://www.geog.leeds.ac.uk/people/a.evans/">Andy Evans</A>
*/
 public class IO {


 
	/**
	* Reads an array of Strings from a text file.
	* Each string is a line.
	* Has the advantage you can set the input character set. Default UTF if null.
	* @param filename text file to read
	* @param charset text character set
	* @return data read in
	*/
	public String[] readBinData(String filename, String charset) {

		File f = new File(filename);
		if (charset == null) charset = "UTF-8";
	  
		FileReader fr = null;
		
		try {
			fr = new FileReader(f);
		} catch  (FileNotFoundException fe) {
			fe.printStackTrace();
		}
		System.out.println(fr.getEncoding());
		
		try {
			fr.close();
		} catch (IOException ioe) {
			ioe.printStackTrace();
		}
		Reader r = null;

		try {

				r = new InputStreamReader(new FileInputStream(f), charset);

		} catch (FileNotFoundException fnfe) {
				fnfe.printStackTrace();
		} catch (UnsupportedEncodingException ue) {
				ue.printStackTrace();
		}

		BufferedReader br = new BufferedReader(r);

		int lines = -1;
		String textIn = " ";
		String[] file = null;

		try {
			while (textIn != null) {
				textIn = br.readLine();
				lines++;
			}

			file = new String[lines];

			br.close();
			try {

				r = new InputStreamReader(new FileInputStream(f), "UTF-8");

			} catch (FileNotFoundException fnfe) {
					fnfe.printStackTrace();
			}
			br = new BufferedReader(r);

			for (int i = 0; i < lines; i++) {
				file[i] = br.readLine();
			}
			
			br.close();
			
		} catch (IOException ioe) {}

		

		return file;
	}

   
   
   
    /**
	* Write an array of Strings to a text file.
	* Each String is a line.
	* Has the advantage you can set the data character format. Default is "ISO-8859-1" if null.
	* @param filename file to write
	* @param data Strings to write
	* @param charset character set
	*/
   public void writeBinData(String filename, String[] data, String charset) {
   
		File f = new File(filename);
	  if (charset == null) charset = "ISO-8859-1";
		

		FileOutputStream fw = null;


		try {

				fw = new FileOutputStream (f, true);

		} catch (IOException ioe) {
				ioe.printStackTrace();
		}

		
				
		String tempStr = "";
		byte[] chars = null;
		try {
			for (int i = 0; i < data.length; i++) {
				chars = data[i].getBytes(Charset.forName(charset));
				System.out.println(chars);
				fw.write(chars);
			}
			fw.close();

		} catch (IOException ioe) {}

   }
   
   
   
   
   /**
	* Reads an array of Strings from a text file.
	* File delimiters are commas and spaces.
	* @param filename text file to read
	* @delim delimiter to use between text
	* @return data read in
	*/
	public String[][] readData(String filename, String delim) {

		File f = new File(filename);
		// Count lines
		
		FileReader fr = null;

		try {

				fr = new FileReader (f);

		} catch (FileNotFoundException fnfe) {
				fnfe.printStackTrace();
		}

		
		BufferedReader br = new BufferedReader(fr);

		int lines = -1;
		String textIn = " ";
		String[] file = null;

		try {
			while (textIn != null) {
				textIn = br.readLine();
				lines++;
			}

			file = new String[lines];

			br.close();
			try {

				fr = new FileReader (f);

			} catch (FileNotFoundException fnfe) {
					fnfe.printStackTrace();
			}
			
			// Read lines.
			
			br = new BufferedReader(fr);

			for (int i = 0; i < lines; i++) {
				file[i] = br.readLine();
			}
			
			br.close();
			
		} catch (IOException ioe) {}

		// Convert lines to doubles.
		
		String[][] data = new String [lines][];

		for (int i = 0; i < lines; i++) {

			StringTokenizer st = new StringTokenizer(file[i],delim);
			data[i] = new String[st.countTokens()];
			int j = 0;
			while (st.hasMoreTokens()) { 		
				data[i][j] = st.nextToken(); 
				j++;
			}
		} 

		return data;
   }

   
   
   
   	/**
	* Write an array of Strings to a text file.
	* Data delimiter is commas and space.
	* @param filename text file to write
	* @param dataIn data to write
	*/
   public void writeData (String filename, String[][] dataIn) {
   
		File f = new File(filename);
		
		FileWriter fw = null;

		try {

				fw = new FileWriter (f, false);

		} catch (IOException ioe) {
				ioe.printStackTrace();
		}

		BufferedWriter bw = new BufferedWriter (fw);
				
		String tempStr = "";

		try {
			for (int i = 0; i < dataIn.length; i++) {
				for (int j = 0; j < dataIn[i].length; j++) {

					tempStr = dataIn[i][j]; 
					bw.write(tempStr + " ");

				}
				bw.newLine();	
			}
			bw.close();

		} catch (IOException ioe) {}


   }


} 