on(construct){
   loop2:
   while(true)
   {
      while(true)
      {
         if(false)
         {
            if(!(0x36F02B2C & 0x36F02B2C))
            {
               §§goto(addr1b4c1);
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
      §§goto(addr1b5ea);
   }
   addr1b551:
   if(ord("\b"))
   {
      §§push("_");
      §§push(false);
      while(true)
      {
         set(§§pop(),§§pop());
         set("\x05",false);
         set("\x12{invalid_utf8=157}\x02",false);
         set("{invalid_utf8=160}",true);
         §§push("{invalid_utf8=136}\x04");
         §§push(true);
         if(!(getTimer() + 1))
         {
            §§pop()[§§pop()] = §§pop();
            while(true)
            {
               set(§§pop(),§§pop());
               set("\x1d{invalid_utf8=150}\x04","\b\x02\x05");
               set("\x1d{invalid_utf8=150}\x04","\b\x02\x05");
               set("\b\x03\x05\x01\x1d{invalid_utf8=150}\x04","\b\x02\x05");
               §§push("\b\x04\x05\x014P{invalid_utf8=157}\x02");
               §§push(true);
               break loop3;
               §§pop() extends §§pop();
            }
            break loop3;
            addr1b4e9:
         }
         set(§§pop(),§§pop());
         set("\x01",-1);
         _ = "\x1d";
         set("{invalid_utf8=150}\x04",0);
         set("\b",true);
         set("\x05",false);
         §§push("\x1d{invalid_utf8=150}\x04");
         §§push("\b\x01\x05");
         if(getTimer())
         {
            §§goto(addr1b4e9);
         }
         §§goto(addr1b551);
         §§push("_");
         §§push(false);
      }
      break loop3;
      addr1b4c1:
   }
   §§pop() extends §§pop();
   addr1b5ea:
}
