on(construct){
   loop2:
   while(true)
   {
      loop3:
      while(true)
      {
         if(!ord("\x02"))
         {
            if(!ord("\x02"))
            {
               while(true)
               {
                  set(§§pop(),§§pop());
                  set("","");
                  set("","\x1d{invalid_utf8=150}\x07");
                  set("\b\r\x07\x04","");
                  §§push("");
                  §§push("\x1d{invalid_utf8=150}\x07");
                  §§goto(addr12ffb);
                  break loop3;
                  §§push(§§pop()(§§pop()));
                  continue loop1;
               }
               §§goto(addr12ffa);
            }
         }
         else
         {
            §§push(478784227);
         }
         if(!§§pop())
         {
            break;
         }
         break loop2;
      }
      break loop1;
   }
   addr12e98:
   if(ord("\x06"))
   {
      set("{invalid_utf8=150}\x05","\x07㪉\x1c{invalid_utf8=157}\x02");
      set("{invalid_utf8=247}","{invalid_utf8=136}\t");
      set("\x03","{invalid_utf8=136}\t");
      set("\x15","{invalid_utf8=196}");
      set("\x03{invalid_utf8=159}",20);
      set("\x1d{invalid_utf8=150}\x07","\b\x15\x07\x14");
      §§push("");
      §§push(true);
      if(ord("\x03"))
      {
         while(true)
         {
            set(§§pop(),§§pop());
            set("",false);
            set("\x1d{invalid_utf8=150}\x04",0);
            set("\b\x16\b\x17\x1d{invalid_utf8=150}\x04",4);
            set("\b\x18\b\x19\x1d{invalid_utf8=150}\x04",0);
            while(true)
            {
               §§push("\b\x1a\b\x1b\x1d{invalid_utf8=150}\x04");
               §§push(0);
               if(!getTimer())
               {
                  §§push(new §\§\§pop()§());
               }
               else
               {
                  set(§§pop(),§§pop());
                  set(§§constant(16),4);
                  set(§§constant(17),4);
                  set(§§constant(18),§§constant(19));
                  §§push(§§constant(20));
                  §§push(10);
                  if(getTimer() + 1)
                  {
                     break loop3;
                  }
                  §§pop() extends §§pop();
                  §§goto(addr12e98);
               }
               §§goto(addr12e1a);
            }
            §§goto(addr12e61);
         }
         break loop3;
      }
      §§pop()[§§pop()] = §§pop();
      §§goto(addr12e61);
   }
   addr12ffa:
   setProperty(§§pop(), _X, §§pop());
   addr12ffb:
   set(§§pop(),§§pop());
   set(§§constant(30),§§constant(31));
   set(§§constant(32),false);
   set(§§constant(33),false);
   set(§§constant(34),false);
   set(§§constant(35),false);
   §§push(§§constant(36));
   §§push(false);
   if(!getTimer())
   {
      §§pop()[§§pop()] = §§pop();
   }
   else
   {
      addr12e61:
      §§goto(addr13032);
   }
   addr13032:
   set(§§pop(),§§pop());
}
