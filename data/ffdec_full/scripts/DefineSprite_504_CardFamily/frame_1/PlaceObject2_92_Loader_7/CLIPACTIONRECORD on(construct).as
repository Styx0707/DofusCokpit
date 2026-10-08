on(construct){
   loop1:
   while(true)
   {
      if(!(0x1BD4CB27 & 0x1BD4CB27))
      {
         if(!ord("\x07"))
         {
            break;
         }
      }
      else
      {
         §§push("\b");
      }
      if(!ord(§§pop()))
      {
         break;
      }
      addr38841:
      while(true)
      {
         if(!(getTimer() + 1))
         {
            setProperty(§§pop(), _X, §§pop());
            break;
         }
         autoLoad = true;
         centerContent = false;
         contentPath = "";
         enabled = false;
         fallbackContentPath = "";
         §§push("forceReload");
         §§push(false);
         break loop1;
         setProperty(§§pop(), _X, §§pop());
      }
      return;
   }
   set(§§pop(),§§pop());
   set("\x10",true);
   set("{invalid_utf8=167}","\x1d{invalid_utf8=150}\x04");
   §§goto(addr38841);
}
