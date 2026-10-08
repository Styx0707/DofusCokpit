on(construct){
   while(true)
   {
      if(!(0x0A6ACCEE & 0x0A6ACCEE))
      {
         if(false)
         {
            break;
         }
      }
      else
      {
         §§push("\x07");
      }
      if(!ord(§§pop()))
      {
         break;
      }
      set("\x16\x18\x14",false);
      contentPath = "none";
      enabled = true;
      set("\x18\f\t",false);
      styleName = "DarkBrownWindow";
      §§push("title");
      §§push("");
      if(!(getTimer() + 1))
      {
         §§goto(addr126e8);
      }
      break;
   }
   set(§§pop(),§§pop());
   addr126e8:
   getProperty(§§pop(), _X);
}
