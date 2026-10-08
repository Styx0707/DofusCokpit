on(construct){
   loop1:
   while(true)
   {
      while(true)
      {
         if(!ord("\x04"))
         {
            if(!(true and true))
            {
               break;
            }
         }
         else
         {
            §§push(true);
         }
         var _temp_1 = §§pop();
         if(_temp_1 and _temp_1)
         {
            break loop1;
         }
         §§goto(addr1df00);
      }
      while(true)
      {
         set("\x05\x01L\x10{invalid_utf8=157}\x02",false);
         set("{invalid_utf8=151}",false);
         set("{invalid_utf8=136}\x06",true);
         set("\x02",false);
         set("\x19",-1);
         §§push("{invalid_utf8=140}");
         §§push("{invalid_utf8=150}\x04");
         if(!(getTimer() + 1))
         {
            break;
         }
         set(§§pop(),§§pop());
         set(§§constant(8),0);
         set(§§constant(9),true);
         set(§§constant(10),false);
         set(§§constant(11),§§constant(12));
         set(§§constant(13),§§constant(14));
         §§push(§§constant(15));
         §§push(§§constant(14));
         if(!getTimer())
         {
            §§push(new §\§\§pop()§());
            break loop1;
         }
         addr1df42:
         set(§§pop(),§§pop());
         set("\b\x04\x05","\x1d{invalid_utf8=150}\x04");
         set("\x1d{invalid_utf8=150}\x07",true);
         §§goto(addr1e02e);
         set("\x19",false);
      }
      startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
      §§goto(addr1df42);
   }
   if(ord("\x02"))
   {
      addr1df00:
      set("\x19",false);
      break loop2;
   }
   var §§pop() = §§pop();
   addr1e02e:
}
