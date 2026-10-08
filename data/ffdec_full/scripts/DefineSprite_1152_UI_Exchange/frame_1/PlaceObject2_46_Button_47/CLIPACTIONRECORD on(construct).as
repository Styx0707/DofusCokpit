on(construct){
   loop1:
   while(true)
   {
      if(!(0x02149590 & 0x02149590))
      {
         if(!ord("\x06"))
         {
            break;
         }
      }
      else
      {
         §§push(false);
      }
      if(§§pop())
      {
         break;
      }
      addr2d37c:
      while(true)
      {
         if(!(getTimer() + 1))
         {
            §§pop() implements ;
            break;
         }
         backgroundDown = "ButtonCraftDown";
         backgroundUp = "ButtonCraftUp";
         enabled = true;
         icon = "";
         label = "";
         §§push("selected");
         §§push(false);
         if(getTimer() + 1)
         {
            break loop1;
         }
         §§push(getProperty(§§pop(), _X));
      }
      return;
   }
   set(§§pop(),§§pop());
   set("\b\t\b\n\x1d{invalid_utf8=150}\x04","\b\x0b\x05");
   set("\x1d",false);
   §§goto(addr2d37c);
}
