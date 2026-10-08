on(construct){
   while(true)
   {
      if(!(0x20982CD0 & 0x20982CD0))
      {
         if(false)
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
            startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
         }
         backgroundDown = "ButtonCraftDownInvert";
         backgroundUp = "ButtonCraftUpInvert";
         enabled = true;
         icon = "";
         label = "";
         §§push("selected");
         §§push(false);
         if(!getTimer())
         {
            setProperty(§§pop(), _X, §§pop());
            §§goto(addr21351);
         }
      }
      set(§§pop(),§§pop());
      break;
   }
   set("\x1b?","\x1d{invalid_utf8=150}\x04");
   set("\b\t\b\n\x1d{invalid_utf8=150}\x04",false);
   addr21351:
}
