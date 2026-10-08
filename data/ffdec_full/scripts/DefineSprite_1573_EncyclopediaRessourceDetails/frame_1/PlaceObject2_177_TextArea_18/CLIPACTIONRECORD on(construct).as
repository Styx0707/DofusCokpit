on(construct){
   loop2:
   while(true)
   {
      while(true)
      {
         if(!ord("\x06"))
         {
            if(!(0x2C826A9C | 0x2C826A9C))
            {
               §§goto(addra998);
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
         break loop2;
      }
      set(§§pop(),§§pop());
      §§goto(addraac8);
   }
   if(!getTimer())
   {
      addraa8e:
      duplicateMovieClip(§§pop(),§§pop(),§§pop());
      set(§§pop(),§§pop());
      maxChars = -1;
      restrict = "none";
      set("\x1a\x11\x13",0);
      set("\x1a\x11\x14",true);
      §§push("selectable");
      §§push(false);
      while(true)
      {
         set(§§pop(),§§pop());
         set("\b\x0f\b\x0e\x1d{invalid_utf8=150}\x04","\b\x10\b\x0e\x1d{invalid_utf8=150}\x04");
         set("\b\x11\x05\x01{invalid_utf8=150}\x02","\x05\x01{invalid_utf8=157}\x02");
         set("{invalid_utf8=204}{invalid_utf8=255}\'{invalid_utf8=150}\x04","\x05\x01{invalid_utf8=157}\x02");
         set("\b","\x05\x01{invalid_utf8=157}\x02");
         §§push("\x05");
         §§push(true);
         break loop3;
         startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
         do
         {
            set("{invalid_utf8=150}\x02",false);
            set("\x05",false);
            set("\x12{invalid_utf8=157}\x02",false);
            o = true;
            §§push("{invalid_utf8=136}\x04");
            §§push(true);
            if(false)
            {
               §§push(getProperty(§§pop(), _X));
               continue;
            }
            §§goto(addraa8f);
         }
         while(getTimer());
         §§goto(addraa8e);
         addraa8f:
      }
      addraac8:
      return;
      addra998:
      §§goto(addraac8);
      §§push(new §\§\§pop()§());
   }
   §§goto(addra9cb);
}
