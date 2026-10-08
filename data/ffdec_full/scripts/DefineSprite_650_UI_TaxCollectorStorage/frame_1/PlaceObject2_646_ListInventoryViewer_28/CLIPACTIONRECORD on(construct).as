on(construct){
   loop4:
   while(true)
   {
      loop5:
      while(true)
      {
         if(!(true and true))
         {
            if(!ord("\n"))
            {
               while(true)
               {
                  set("\x05\x01{invalid_utf8=157}\x02",true);
                  set("W{invalid_utf8=255}<\x1d",false);
                  set("\x1d{invalid_utf8=150}\x07",true);
                  set("\b\x17\x01",false);
                  set("",false);
                  §§push("");
                  §§push(true);
                  if(!ord("\x06"))
                  {
                     §§goto(addr14dab);
                     §§push(getProperty(§§pop(), _X));
                  }
                  §§goto(addr14e18);
                  break loop5;
               }
               §§goto(addr14e17);
               addr14d6f:
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
         break loop4;
      }
      set(§§pop(),§§pop());
      §§goto(addr14d6f);
   }
   if(getTimer() + 1)
   {
      loop3:
      do
      {
         Pl = true;
         set("{invalid_utf8=200}",false);
         set(§§constant(2),§§constant(3));
         set(§§constant(4),true);
         set(§§constant(5),§§constant(3));
         §§push(§§constant(6));
         §§push(false);
         if(false)
         {
            §§push(getProperty(§§pop(), _X));
            continue;
         }
         addr14dab:
         while(true)
         {
            set(§§pop(),§§pop());
            set("\x1d{invalid_utf8=150}\x04",true);
            set("\b\'\x05\x01\x1d{invalid_utf8=150}\x04","\b(\x05");
            set("\x1d{invalid_utf8=150}\x04","\b)\x05\x01\x1d{invalid_utf8=150}\x04");
            set("\b*\x05","\x1d{invalid_utf8=150}\x04");
            §§push("\b+\x05");
            §§push("\x1d{invalid_utf8=150}\x04");
            if(!getTimer())
            {
               break;
            }
            while(true)
            {
               set(§§pop(),§§pop());
               set(§§constant(15),§§constant(16));
               set(§§constant(17),20);
               set(§§constant(18),§§constant(19));
               set(§§constant(20),false);
               set(§§constant(21),0);
               §§push(§§constant(22));
               §§push(4);
               if(!getTimer())
               {
                  break;
               }
               set(§§pop(),§§pop());
               set("\x18\x12\x14",0);
               set("\x18\x12\x15",0);
               set("\x18\x15\x18",4);
               set("\x18\x15\x19",4);
               set("\x18\x1c\x01","this._parent._parent");
               §§push("\x1a\x0f\x01");
               §§push(10);
               if(ord("\x05"))
               {
                  addr14dda:
                  set(§§pop(),§§pop());
                  set("",20);
                  set("","\x1d{invalid_utf8=150}\x04");
                  set("\b\x1f\b \x1d{invalid_utf8=150}\x04","\b!\b\"\x1d{invalid_utf8=150}\x04");
                  set("\b#\b$\x1d{invalid_utf8=150}\x04","\b%\b\x03\x1d{invalid_utf8=150}\x04");
                  set("\b&\x05","|\x01{invalid_utf8=136}\x07");
                  §§push("{invalid_utf8=150}\x02");
                  §§push(false);
                  if(false)
                  {
                     addr14e17:
                     var §§pop() = §§pop();
                     addr14e18:
                     set(§§pop(),§§pop());
                     §§goto(addr1509a);
                  }
                  break loop5;
               }
               var §§pop() = §§pop();
            }
            §§pop()[§§pop()] = §§pop();
            continue loop3;
         }
         §§pop()[§§pop()] = §§pop();
         §§goto(addr14dda);
      }
      while(getTimer() + 1);
   }
   addr1509a:
}
