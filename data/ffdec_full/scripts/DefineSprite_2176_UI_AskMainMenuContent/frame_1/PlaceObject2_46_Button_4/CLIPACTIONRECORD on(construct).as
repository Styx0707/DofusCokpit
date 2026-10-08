on(construct){
   while(true)
   {
      if(!(0x1D97AD50 | 0x1D97AD50))
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
      if(!§§pop())
      {
         if(!(getTimer() + 1))
         {
            §§pop()[§§pop()] = §§pop();
         }
         backgroundDown = "ButtonNormalDown";
         backgroundUp = "ButtonNormalUp";
         enabled = true;
         icon = "";
         §§push("label");
         §§push("");
         if(false)
         {
            §§goto(addr2deec);
         }
      }
      set(§§pop(),§§pop());
      break;
   }
   set("\b\b\x05",false);
   set("\x1d{invalid_utf8=150}\x04","\b\t\b\n\x1d{invalid_utf8=150}\x04");
   set("\b\x0b\x05",false);
   addr2deec:
   getProperty(§§pop(), _X);
}
