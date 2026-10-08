on(construct){
   while(true)
   {
      if(!ord("\x02"))
      {
         if(!(0x0161DED0 | 0x0161DED0))
         {
            break;
         }
      }
      else
      {
         §§push("\x04");
      }
      if(!ord(§§pop()))
      {
         break;
      }
      if(!ord("\n"))
      {
         startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
      }
      backgroundDown = "ButtonCraftDown";
      backgroundUp = "ButtonCraftUp";
      enabled = true;
      icon = "";
      label = "";
      §§push("selected");
      §§push(false);
      if(!(getTimer() + 1))
      {
         §§goto(addr8a48);
      }
      break;
   }
   set(§§pop(),§§pop());
   set("\x0e{invalid_utf8=147}","\x1d{invalid_utf8=150}\x04");
   set("\b\t\b\n\x1d{invalid_utf8=150}\x04",false);
   addr8a48:
   getProperty(§§pop(), _X);
}
