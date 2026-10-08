on(construct){
   loop1:
   while(true)
   {
      while(true)
      {
         if(!ord("\n"))
         {
            if(!(0x23A9FA8D & 0x23A9FA8D))
            {
               §§goto(addr7087);
            }
         }
         else
         {
            §§push(107683797);
         }
         if(!§§pop())
         {
            break;
         }
         break loop1;
      }
      set(§§pop(),§§pop());
      set(§§constant(8),§§constant(9));
      §§goto(addr7145);
   }
   while(true)
   {
      set("{invalid_utf8=150}\x05",true);
      set("\x07{invalid_utf8=213}\x1fk\x06{invalid_utf8=157}\x02",true);
      V = "{invalid_utf8=136}\x07";
      set("\x02",false);
      set("{invalid_utf8=185}","{invalid_utf8=136}\x07");
      set("3\n",false);
      §§push("\x1d{invalid_utf8=150}\x04");
      §§push(false);
      break loop2;
      §§pop() extends §§pop();
      §§goto(addr70c9);
      addr70c9:
   }
   addr7145:
   return;
   addr7087:
   var §§pop() = §§pop();
   §§goto(addr7145);
}
