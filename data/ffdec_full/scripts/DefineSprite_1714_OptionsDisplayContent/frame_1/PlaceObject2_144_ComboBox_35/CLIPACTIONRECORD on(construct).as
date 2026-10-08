on(construct){
   loop2:
   while(true)
   {
      loop3:
      while(true)
      {
         if(!(0x2CF580C5 & 0x2CF580C5))
         {
            if(!(true or true))
            {
               while(true)
               {
                  set("\b\x10\x07\x04",0);
                  set("",4);
                  set("",4);
                  §§push("\x1d{invalid_utf8=150}\x07");
                  §§push("\b\x11\x07\x04");
                  if(!ord("\x07"))
                  {
                     §§goto(addr28894);
                     §§push(§§pop()());
                  }
                  §§goto(addr288cb);
                  break loop3;
               }
               §§goto(addr288ca);
               addr2885f:
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
      §§goto(addr2885f);
   }
   if(getTimer() + 1)
   {
      do
      {
         set("{invalid_utf8=150}\x02","\x05");
         set("\x12{invalid_utf8=157}\x02","{invalid_utf8=218}");
         set("{invalid_utf8=136}\t","{invalid_utf8=218}");
         set("\x03","9");
         §§push("{invalid_utf8=201}");
         §§push(20);
         if(!ord("\n"))
         {
            addr288ca:
            §§pop() implements ;
            addr288cb:
            set(§§pop(),§§pop());
            set("",3);
            set("",20);
            set("\x1d{invalid_utf8=150}\x04","\b\x12\b\x13{invalid_utf8=150}\x03");
            §§goto(addr28a28);
         }
         set(§§pop(),§§pop());
         set(§§constant(8),§§constant(9));
         set(§§constant(10),true);
         set(§§constant(11),false);
         set(§§constant(12),0);
         set(§§constant(13),4);
         §§push(§§constant(14));
         §§push(0);
         if(getTimer() + 1)
         {
            break loop3;
         }
         setProperty(§§pop(), _X, §§pop());
      }
      while(getTimer() + 1);
      addr28894:
   }
   addr28a28:
}
