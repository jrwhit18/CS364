if
  	;)  ( 12345    // the tokens ; ) 12345


  	fred zoo    		identifier   // three identifiers

  	rewhilemi

    // all keywords  	
  	bool else if print false true int main while char float   // this is a comment
  	
	// the tokens && is one token as are <=, >=, ==, !=, ||
  	123 < 34.567 && true <=    >= < >  ==    =  || [] / * !=  , {} 
   =  =   <  
  	int a,b;   // five tokens
   	
        _9ident = -3.14159

  	>><<   // two separate tokens << and >>
  	
  	{

        "a string literal" // followed by a comment

  	}
  	
  	!
  	
  	|| %  - * + 
  	
	
  	
  	// illegal tokens below

  	3.4.5    // illegal, not a valid floating-point identifier   
	4a       // illegal, not a valid identifier 
	"        // illegal, missing closing quote  
	? @#$  'a' ^ ~ ` :  // all gibberish  
	
	//////////////////////////////////////////////////////////////////////
	// FOR 100 POINTS
	//////////////////////////////////////////////////////////////////////
	
	// Up until this point you can get a 90 
	// The tests below will get you a 100
	
	// python allows underscores in numbers for legibility. The
	// token below are legitimate
	123_456_789 and 3.141_592_653_589_793     
	
	// scientific notation
	3e-9  // 3 times ten to the minus 9
	-2.34e9  // two tokens! - and 2.34e9
	
	// scientific notation can use underscores
	3_123.456_789e-1_2
	
	_123_456   // this is an identifier
	123_       // illegal, cannot end with an underscore
	
	// what about a comment in a string literal?
	print("// this is a string literal, not a comment");
	
	// a string literal in a comment should be OK
    // this is a "comment and not a string literal"
	
	// you can have illegal characters in a comment user@email.com `@# '
	
	"illegal characters in a string user@email.com `@# ' "
	
	// even ill-formed string literal in a comment should be OK
	// this is a "comment and is ok, even with closing double quote missing
	
	"a string // literal" "// and another"   // two string lit tokens
	
	"a string \"literal\" that contains \"escaped\" double quotes"  // one token
	