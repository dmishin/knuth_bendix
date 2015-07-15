#Generates JS code that effectively rewrites

__doc__ = """
Every string is a sequence of powers of 2 operators: A and B.
powers are limited to be in range -n/2 ... n/2 and -m/2 ... m/2


rewrite rules work on these pow cahins:


Trivial rewrites:
   a^-1 a       -> e
   b^-1 b       -> e
   a a^-1       -> e
   b b^-1       -> e

Non-trivial ones:


 Ending with b
   a b  -> b^-1 a^-1
   b^2  -> b^-2
   b^-1 a^-1 b^-1       -> a
   b^-3 -> b
   a b^-2       -> b^-1 a^-1 b
   b a^-1 b^-1  -> b^-2 a

 Ending with a
   a^2  -> a^-2
   b a  -> a^-1 b^-1
   a^-3 -> a
   a^-1 b^-1 a^-1       -> b
   a b^-1 a^-1  -> a^-2 b
   b a^-2       -> a^-1 b^-1 a


Idea: 2 rewriters. For chains ending with A and with B.


Chains are made in functional style, stored from end. 

function NodeA( p, tail ){ this.p = p; this.t=tail; };
function NodeB( p, tail ){ this.p = p; this.t=tail; };


/*How it can be implemented:*/

function endsA_appendA( chain, powerA )
{
    //append a^powerA to the chain
    var power1 = chain.p + powerA;
    if (power1 == 0){
        return chain.t; //return tail
    }
    var chain1 = new NodeA( power1, chain.t );
    return endsA_rewrite(chain1);    
}
function endsA_appendB( chain, powerB )
{
    return endsB_rewrite( new NodeB( powerB, chain ) );
}

//rewrite the freshly appended chain. 
/*

  sorted by power
*  a^2  -> a^-2   # -4
   b a  -> a^-1 b^-1

*  a^-3 -> a      # +4

   b a^-2       -> a^-1 b^-1 a
   a^-1 b^-1 a^-1       -> b
   a b^-1 a^-1  -> a^-2 b
*/
function endsA_rewrite( chain )
{
   if (chain.p > 0){
       //positive power...
   }else{
       //negative power...  

       //special case (these should be 1 of these...) power of a -> power of a.
       //a^2  -> a^-2
       if (chain.p >= 2){
           chain.p -= 2;
   }
}

How to impleent 
