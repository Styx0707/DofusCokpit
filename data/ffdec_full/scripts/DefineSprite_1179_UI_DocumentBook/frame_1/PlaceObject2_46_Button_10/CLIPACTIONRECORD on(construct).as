on(construct){
   while(true)
   {
      if(!(0x08486EF0 | 0x08486EF0))
      {
         if(!(true or true))
         {
            break;
         }
      }
      else
      {
         §§push("\x0b");
      }
      if(!ord(§§pop()))
      {
         break;
      }
      if(!ord("\x04"))
      {
         setProperty(§§pop(), _X, §§pop());
      }
      backgroundDown = "ButtonBookPageRightDown";
      backgroundUp = "ButtonBookPageRightUp";
      enabled = true;
      icon = "";
      label = "";
      §§push("selected");
      §§push(false);
      if(!ord("\n"))
      {
         §§pop()[§§pop()] = §§pop();
         §§goto(addr2bee);
      }
      break;
   }
   set(§§pop(),§§pop());
   set("\x1d{invalid_utf8=150}\x04","\b\t\b\n\x1d{invalid_utf8=150}\x04");
   set("\b\x0b\x05",false);
   addr2bee:
}
