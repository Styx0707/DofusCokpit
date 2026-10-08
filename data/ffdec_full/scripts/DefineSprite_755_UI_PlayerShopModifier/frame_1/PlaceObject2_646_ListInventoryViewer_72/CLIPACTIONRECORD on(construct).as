on(construct){
   loop3:
   while(true)
   {
      while(true)
      {
         if(!ord("\x0b"))
         {
            if(false)
            {
               break;
            }
         }
         else
         {
            §§push(true);
         }
         var _temp_1 = §§pop();
         if(!(_temp_1 and _temp_1))
         {
            break;
         }
         break loop3;
      }
      break loop1;
   }
   addr15f4d:
   if(!ord("\x05"))
   {
      var §§pop() = §§pop();
      while(true)
      {
         set(§§pop(),§§pop());
         set("\x18\x12\x13",4);
         set("\x18\x12\x14",0);
         set("\x18\x12\x15",0);
         set("\x18\x15\x18",4);
         §§push("\x18\x15\x19");
         §§push(4);
         if(false)
         {
            §§goto(addr1614a);
         }
         set(§§pop(),§§pop());
         set(§§constant(27),§§constant(28));
         set(§§constant(29),10);
         set(§§constant(30),20);
         set(§§constant(31),§§constant(32));
         set(§§constant(33),§§constant(34));
         §§push(§§constant(35));
         §§push(§§constant(36));
         if(getTimer())
         {
            break loop4;
         }
         setProperty(§§pop(), _X, §§pop());
         §§goto(addr15f4d);
         var §§pop() = §§pop();
      }
      §§goto(addr15e85);
   }
   while(true)
   {
      set("{invalid_utf8=150}\x02",true);
      set("\x05\x01L\x10{invalid_utf8=157}\x02",false);
      set("5\x01{invalid_utf8=136}\x07","\x02");
      e = true;
      set("i\x15","\x02");
      while(true)
      {
         §§push("\x1d{invalid_utf8=150}\x04");
         §§push(false);
         if(!(getTimer() + 1))
         {
            §§pop() implements ;
         }
         else
         {
            set(§§pop(),§§pop());
            set(§§constant(7),true);
            set(§§constant(8),§§constant(9));
            set(§§constant(10),§§constant(11));
            §§push(§§constant(12));
            §§push(§§constant(13));
            if(false)
            {
               var §§pop() = §§pop();
               §§goto(addr15f10);
            }
         }
         addr15e85:
         set(§§pop(),§§pop());
         z = "\b)\x05\x014P{invalid_utf8=157}\x02";
         set("\"{invalid_utf8=150}\x04","\b");
         set("\x05\x01\x1d{invalid_utf8=150}\x04",20);
         set("\b\x01\x05","\x1d{invalid_utf8=150}\x04");
         set("\b\x02\b\x03\x1d{invalid_utf8=150}\x04",false);
         §§goto(addr16108);
      }
      addr16108:
      §§push("\b\x04\x05\x01\x1d{invalid_utf8=150}\x04");
      §§push(0);
      §§goto(addr16108);
      setProperty(§§pop(), _X, §§pop());
      set(§§pop(),§§pop());
      set("\x12{invalid_utf8=157}\x02",false);
      set(">\x02#\x1d{invalid_utf8=150}\x04",true);
      set("\b*\x05",true);
      addr1614a:
      new §\§\§pop()§();
      return;
   }
   break loop4;
}
