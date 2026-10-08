on(construct){
   loop3:
   while(true)
   {
      while(true)
      {
         if(false)
         {
            if(!ord("\b"))
            {
               §§goto(addr28a20);
            }
         }
         else
         {
            §§push(310007746);
         }
         if(!§§pop())
         {
            break;
         }
         break loop3;
      }
      set(§§pop(),§§pop());
      §§goto(addr28b4d);
   }
   while(true)
   {
      set("{invalid_utf8=150}\x05",false);
      set("\x07{invalid_utf8=194}Wz\x12{invalid_utf8=157}\x02",false);
      set("{invalid_utf8=164}",false);
      set("{invalid_utf8=136}\x06",true);
      set("\x02",false);
      L = -1;
      §§push("{invalid_utf8=177}");
      §§push("\x1d");
      if(getTimer() + 1)
      {
         break;
      }
      §§pop()[§§pop()] = §§pop();
      §§goto(addr28ab8);
      addr28ab8:
   }
   loop1:
   while(true)
   {
      set(§§pop(),§§pop());
      set("\x1d{invalid_utf8=150}\x04",0);
      set("\b\r\b\x0e\x1d{invalid_utf8=150}\x04",true);
      set("\b\x0f\b\x0e\x1d{invalid_utf8=150}\x04",false);
      §§push("\b\x10\b\x0e\x1d{invalid_utf8=150}\x04");
      §§push("\b\x11\x05\x01{invalid_utf8=150}\x03");
      if(getTimer())
      {
         set(§§pop(),§§pop());
         while(true)
         {
            set("","\x0b");
            set("2{invalid_utf8=157}\x02","\x0b");
            set("{invalid_utf8=210}{invalid_utf8=255}@\x1d{invalid_utf8=150}\x07","\x0b");
            §§push("\b\b\x01");
            §§push(true);
            if(ord("\x0b"))
            {
               break loop4;
            }
            §§push(new §\§\§pop()§());
            continue loop1;
            set(§§pop(),§§pop());
         }
         break loop4;
         addr28a20:
      }
      §§pop()[§§pop()] = §§pop();
      §§goto(addr28a76);
      addr28a76:
   }
   addr28b4d:
   new §\§\§pop()§();
}
