on(construct){
   loop1:
   while(true)
   {
      if(!ord("\x02"))
      {
         if(!(0x1C232373 & 0x1C232373))
         {
            break;
         }
      }
      else
      {
         §§push("\x03");
      }
      if(!ord(§§pop()))
      {
         break;
      }
      addr1a7c5:
      while(true)
      {
         if(!getTimer())
         {
            startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
            break;
         }
         backgroundDown = "ButtonCrossDown";
         backgroundUp = "ButtonCrossUp";
         enabled = true;
         icon = "";
         label = "";
         §§push("selected");
         §§push(false);
         if(ord("\x05"))
         {
            break loop1;
         }
         §§pop() implements ;
      }
      return;
   }
   set(§§pop(),§§pop());
   set("\b\t\b\n\x1d{invalid_utf8=150}\x04","\b\x0b\x05");
   set("\x1d",false);
   §§goto(addr1a7c5);
}
