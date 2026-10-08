on(construct){
   loop1:
   while(true)
   {
      if(!(0x1DB002FA & 0x1DB002FA))
      {
         if(!(0x1DB002FA | 0x1DB002FA))
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
      addrcb30:
      while(true)
      {
         if(!ord("\x03"))
         {
            §§pop()[§§pop()] = §§pop();
            break;
         }
         backgroundDown = "ButtonCraftDown";
         backgroundUp = "ButtonCraftUp";
         enabled = false;
         icon = "";
         label = "";
         §§push("selected");
         §§push(false);
         if(ord("\x07"))
         {
            break loop1;
         }
         §§push(getProperty(§§pop(), _X));
      }
      return;
   }
   set(§§pop(),§§pop());
   set("\x1d{invalid_utf8=150}\x04","\b\t\b\n\x1d{invalid_utf8=150}\x04");
   set("\b\x0b\x05",false);
   §§goto(addrcb30);
}
