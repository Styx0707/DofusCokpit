on(construct){
   while(true)
   {
      if(!(0x1C1EB679 & 0x1C1EB679))
      {
         if(!ord("\n"))
         {
            break;
         }
      }
      else
      {
         §§push("\x02");
      }
      if(ord(§§pop()))
      {
         if(!ord("\n"))
         {
            startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
         }
         backgroundRenderer = "";
         set("\x16\x10\x12","");
         dragAndDrop = true;
         enabled = true;
         §§push("\x18\x07\x0e");
         §§push(true);
         if(!ord("\x04"))
         {
            setProperty(§§pop(), _X, §§pop());
            §§goto(addr3b13);
         }
      }
      set(§§pop(),§§pop());
      set(§§constant(6),"{invalid_utf8=142}{invalid_utf8=136}");
      break;
   }
   set("\'",1);
   set("{invalid_utf8=142}{invalid_utf8=136}",2);
   set("{invalid_utf8=131}{invalid_utf8=170}",false);
   set("\x1d{invalid_utf8=150}\x04","\b\x06\b\x01\x1d{invalid_utf8=150}\x07");
   addr3b13:
}
