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

import java.util.regex.*;


/**
* Converts emoji scattered text to text with descriptions of emoji.
* Arguments should be text file to read, then text file to write, then character to delimit start 
* of emoji and character to delimit end of emoji. Character cannot be asterisk, so this is default. 
* Works off two files that must be in same 
* directory -- emoji.csv, containing emoji information and standard.csv containing any standard 
* UTF-8 16bit replacement strings that need replacing but not with delimiters.
* Files should be UTF-8 16bit \\uxxxx\\uxxxx style strings in column 0, and the replacement text in 
* column 1 of a 2-column text file.
* Emoji list currently forked from https://github.com/iamcal/js-emoji/blob/master/emoji.js
* @version 1.0
* @author <A href="http://www.geog.leeds.ac.uk/people/a.evans/">Andy Evans</A>
*/
public class Convert {

	/** Text to convert. **/
	String text[][] = null;

	/**
	* Converts!
	* @param args see class documentation.
	*/
	public Convert(String[] args) {
	
		if (args.length < 2) {
			System.err.println("Usage: java Convert inputFilename outputFilename emojiIndicatorStart emojiIndicatorEnd");
		}
		
		String emojiDelimiterStart = "*";
		String emojiDelimiterEnd = "*";
		
		if (args.length == 4) {
			emojiDelimiterStart = args[2];
			emojiDelimiterEnd = args[3];
		}
		
		IO io = new IO();
		text = io.readData(args[0], " ");
		String emoji[][] = io.readData("emoji.csv",", ");
		
		
		String utf8String = "";
		Pattern p = null;
		for (int i = 0; i < emoji.length; i++) {
			utf8String = Matcher.quoteReplacement(emoji[i][0]);
			utf8String = Pattern.compile(utf8String, Pattern.CASE_INSENSITIVE | Pattern.UNICODE_CASE).toString();
			replace (utf8String, emojiDelimiterStart + emoji[i][1] + emojiDelimiterEnd);
		}

		String standardChars[][] = io.readData("standard.csv",", ");
		for (int i = 0; i < standardChars.length; i++) {
			utf8String = Matcher.quoteReplacement(standardChars[i][0]);
			utf8String = Pattern.compile(utf8String, Pattern.CASE_INSENSITIVE | Pattern.UNICODE_CASE).toString();
			replace (utf8String, standardChars[i][1]);
		}

		io.writeData(args[1], text);
	
	}



	
	/**
	* Replaces rexex pattern with String in text.
	* @param args see class documentation.
	*/
	private void replace (String oldPattern, String newString) {
		for (int j = 0; j < text.length; j++) {
			for (int k = 0; k < text[j].length; k++) {
				text[j][k] = text[j][k].replaceAll(oldPattern, newString);
			}
		}
	}
	
	
	
	
	/**
	* Converts!
	* @param args see class documentation.
	*/
	public static void main(String args[]) {
	
		new Convert(args);
	
	}
	
}