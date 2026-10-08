on(construct){
   loop1:
   while(true)
   {
      if(!(0x07DA985C & 0x07DA985C))
      {
         if(!ord("\x07"))
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
      addr068b:
      while(true)
      {
         if(!ord("\x03"))
         {
            startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
            break;
         }
         backgroundDown = "ButtonCloseDown";
         backgroundUp = "ButtonCloseUp";
         enabled = true;
         icon = "";
         label = "";
         §§push("selected");
         §§push(false);
         if(ord("\x06"))
         {
            break loop1;
         }
         §§pop()[§§pop()] = §§pop();
      }
      return;
   }
   set(§§pop(),§§pop());
   set("\b\x0b\x05","\x1d");
   set("{invalid_utf8=150}\x04",false);
   §§goto(addr068b);
}
