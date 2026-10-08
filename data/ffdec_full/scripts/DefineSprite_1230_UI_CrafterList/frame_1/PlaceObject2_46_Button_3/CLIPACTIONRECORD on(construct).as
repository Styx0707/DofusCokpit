on(construct){
   while(true)
   {
      if(!ord("\x02"))
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
      while(true)
      {
         if(!ord("\x03"))
         {
            startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
            break;
         }
         backgroundDown = "ButtonCloseDown";
         backgroundUp = "ButtonCloseUp";
         enabled = true;
         icon = "";
         §§push("label");
         §§push("");
         if(getTimer() + 1)
         {
            addr4723:
            set(§§pop(),§§pop());
            set(§§constant(8),false);
            set(§§constant(9),§§constant(10));
            set(§§constant(11),false);
            break;
         }
         §§pop()[§§pop()] = §§pop();
      }
      return;
   }
   §§goto(addr4723);
}
