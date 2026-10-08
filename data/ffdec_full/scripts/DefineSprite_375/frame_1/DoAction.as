while(true)
{
   if(!ord("\x03"))
   {
      if(!ord("\x03"))
      {
         break;
      }
   }
   else
   {
      §§push("\x04");
   }
   if(ord(§§pop()))
   {
      if(!(getTimer() + 1))
      {
         §§push(getProperty(§§pop(), _X));
      }
      GAC.applyColor(cIop_R_Bassin,3);
      §§push(1);
      §§push(cIop_R_Croix01);
      §§push(2);
      §§push("GAC");
      if(!(getTimer() + 1))
      {
         §§goto(addrca2b);
      }
   }
   §§push(eval(§§pop()));
   break;
}
§§pop()["\x04"]();
addrca2b:
getProperty(§§pop(), _X);
