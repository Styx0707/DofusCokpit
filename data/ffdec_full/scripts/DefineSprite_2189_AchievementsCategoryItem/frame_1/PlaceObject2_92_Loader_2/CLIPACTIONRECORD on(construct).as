on(construct){
   while(true)
   {
      if(false)
      {
         if(!(0x2BE017FE & 0x2BE017FE))
         {
            break;
         }
      }
      else
      {
         §§push("\b");
      }
      if(ord(§§pop()))
      {
         if(!ord("\x0b"))
         {
            startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
         }
         autoLoad = true;
         centerContent = false;
         contentPath = "";
         enabled = false;
         §§push("fallbackContentPath");
         §§push("");
         if(!getTimer())
         {
            setProperty(§§pop(), _X, §§pop());
            §§goto(addr181a1);
         }
      }
      set(§§pop(),§§pop());
      §§push(§§constant(6));
      §§push(true);
      break;
   }
   set(§§pop(),§§pop());
   set(",",true);
   x = "\x1d{invalid_utf8=150}\x04";
   addr181a1:
}
