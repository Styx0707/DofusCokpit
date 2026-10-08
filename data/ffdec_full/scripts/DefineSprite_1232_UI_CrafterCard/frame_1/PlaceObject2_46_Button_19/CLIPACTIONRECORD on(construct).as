on(construct){
   loop1:
   while(true)
   {
      if(!(0x06668DB6 & 0x06668DB6))
      {
         if(false)
         {
            break;
         }
      }
      else
      {
         §§push("\x05");
      }
      if(!ord(§§pop()))
      {
         break;
      }
      addrb5b6:
      while(true)
      {
         if(!getTimer())
         {
            §§pop()[§§pop()] = §§pop();
            break;
         }
         backgroundDown = "ButtonCloseDown";
         backgroundUp = "ButtonCloseUp";
         enabled = true;
         icon = "";
         label = "";
         §§push("selected");
         §§push(false);
         if(getTimer())
         {
            break loop1;
         }
         §§pop() extends §§pop();
      }
      return;
   }
   set(§§pop(),§§pop());
   set("{invalid_utf8=182}{invalid_utf8=133}","\x1d{invalid_utf8=150}\x04");
   set("\b\t\b\n\x1d{invalid_utf8=150}\x04",false);
   §§goto(addrb5b6);
}
