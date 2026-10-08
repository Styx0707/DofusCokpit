on(construct){
   loop3:
   while(true)
   {
      loop4:
      while(true)
      {
         if(!ord("\x05"))
         {
            if(!(true or true))
            {
               while(true)
               {
                  set(§§pop(),§§pop());
                  set("",true);
                  set("\x1d{invalid_utf8=150}\x04",316);
                  set("\b\x0f\x05\x01\x1d{invalid_utf8=150}\x04",false);
                  §§push("\b\x10\x05");
                  §§push(false);
                  if(!getTimer())
                  {
                     §§pop() extends §§pop();
                     §§goto(addr4237);
                  }
                  §§goto(addr42a1);
                  break loop4;
               }
               §§goto(addr42a0);
               addr420d:
            }
         }
         else
         {
            §§push(197199191);
         }
         if(!(§§pop() + 1))
         {
            break;
         }
         break loop3;
      }
      set(§§pop(),§§pop());
      §§goto(addr420d);
   }
   if(getTimer())
   {
      loop2:
      do
      {
         set("G}",true);
         set("0",false);
         M = §§constant(3);
         set(§§constant(4),true);
         §§push(§§constant(5));
         §§push(§§constant(3));
         if(!ord("\b"))
         {
            §§push(getProperty(§§pop(), _X));
         }
         else
         {
            set(§§pop(),§§pop());
            M = false;
            set("\x1d{invalid_utf8=150}\x04",true);
            set("\b\x18\x05","\x1d{invalid_utf8=150}\x04");
            set("\b\x19\x05\x01\x1d{invalid_utf8=150}\x07",false);
            set("\b\x1a\x07<\x01",false);
            §§push("");
            §§push(false);
            if(getTimer())
            {
               while(true)
               {
                  set(§§pop(),§§pop());
                  set("\x1d{invalid_utf8=150}\x04",false);
                  set("\b\x1b\x05",0);
                  set("\x1d{invalid_utf8=150}\x04",true);
                  set("\b\x1c\x05",false);
                  §§push("4{invalid_utf8=157}\x02");
                  §§push("\x03");
                  if(getTimer() + 1)
                  {
                     set(§§pop(),§§pop());
                     set(§§constant(18),§§constant(19));
                     set(§§constant(20),§§constant(3));
                     set(§§constant(21),false);
                     set(§§constant(22),false);
                     §§push(§§constant(23));
                     §§push(false);
                     if(getTimer())
                     {
                        break loop4;
                     }
                     §§push(§§pop()());
                     continue loop2;
                  }
                  var §§pop() = §§pop();
                  §§goto(addr426a);
                  addr426a:
               }
               break loop4;
               addr4237:
            }
            addr42a0:
            §§pop() extends §§pop();
            addr42a1:
            set(§§pop(),§§pop());
            set("\x1d{invalid_utf8=150}\x04",false);
            §§goto(addr440e);
         }
      }
      while(getTimer());
   }
   setProperty(§§pop(), _X, §§pop());
   addr440e:
}
