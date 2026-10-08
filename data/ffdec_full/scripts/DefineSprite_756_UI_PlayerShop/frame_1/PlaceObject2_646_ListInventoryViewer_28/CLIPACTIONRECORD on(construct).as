on(construct){
   loop3:
   while(true)
   {
      loop4:
      while(true)
      {
         if(!(0x35FCC82A & 0x35FCC82A))
         {
            if(false)
            {
               while(true)
               {
                  set("",false);
                  set("\t",true);
                  set("2{invalid_utf8=157}\x02",true);
                  set("{invalid_utf8=129}",false);
                  §§push("<\x1d{invalid_utf8=150}\x04");
                  §§push(true);
                  if(!ord("\x02"))
                  {
                     setProperty(§§pop(), _X, §§pop());
                     §§goto(addr6f2d);
                  }
                  §§goto(addr6fc7);
                  break loop4;
               }
               break loop2;
               addr6ef9:
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
         break loop3;
      }
      set(§§pop(),§§pop());
      §§goto(addr6ef9);
   }
   loop5:
   while(true)
   {
      if(!(getTimer() + 1))
      {
         startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
         §§goto(addr7206);
      }
      while(true)
      {
         set("{invalid_utf8=150}\x03",true);
         set("",false);
         set("\x0b","2{invalid_utf8=157}\x02");
         set("]\x01{invalid_utf8=136}\x06",true);
         loop6:
         while(true)
         {
            §§push("\x02");
            §§push("2{invalid_utf8=157}\x02");
            if(!ord("\t"))
            {
               addr6f96:
               var §§pop() = §§pop();
               §§goto(addr6f97);
            }
            set(§§pop(),§§pop());
            set(§§constant(6),false);
            set(§§constant(7),true);
            set(§§constant(8),§§constant(9));
            set(§§constant(10),§§constant(11));
            §§push(§§constant(12));
            §§push(§§constant(13));
            if(ord("\x05"))
            {
               while(true)
               {
                  set(§§pop(),§§pop());
                  set("\x1d{invalid_utf8=150}\x04","\b+\x05");
                  set("\b,\x05\x01{invalid_utf8=150}\x03","");
                  set("\x02",20);
                  set("2{invalid_utf8=157}\x02","{invalid_utf8=155}");
                  §§push("#\x1d{invalid_utf8=150}\x04");
                  §§push(false);
                  if(false)
                  {
                     break loop6;
                  }
                  set(§§pop(),§§pop());
                  set(§§constant(21),0);
                  set(§§constant(22),4);
                  set(§§constant(23),0);
                  set(§§constant(24),0);
                  set(§§constant(25),4);
                  §§push(§§constant(26));
                  §§push(4);
                  if(false)
                  {
                     §§goto(addr701b);
                     §§push(getProperty(§§pop(), _X));
                  }
                  else
                  {
                     addr7206:
                     set(§§pop(),§§pop());
                     set("\x18\x1c\x01","this._parent._parent");
                     set("\x1a\x0f\x01",10);
                     rowHeight = 20;
                     §§push("backgroundDown");
                     §§push("ButtonToggleDown");
                     addr6f97:
                     set(§§pop(),§§pop());
                     set("\b","\x05\x01\x1d{invalid_utf8=150}\x04");
                     set("\b\x01\x05","\x1d{invalid_utf8=150}\x04");
                     set("\b\x02\b\x03\x1d{invalid_utf8=150}\x04","2{invalid_utf8=157}\x02");
                     set("\b\x04\x05\x01\x1d{invalid_utf8=150}\x04",false);
                     §§push("\b\x05\b\x03{invalid_utf8=150}\x03");
                     §§push(true);
                     if(!(getTimer() + 1))
                     {
                        §§push(§§pop()(§§pop()));
                        break loop5;
                     }
                     break loop4;
                  }
                  addr701b:
               }
               §§goto(addr6f96);
               addr6f2d:
            }
            §§push(getProperty(§§pop(), _X));
            continue loop5;
         }
         continue loop5;
         var §§pop() = §§pop();
      }
      startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
      §§goto(addr7237);
   }
   addr6fc7:
   set(§§pop(),§§pop());
   addr7237:
}
