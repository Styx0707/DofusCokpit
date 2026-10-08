on(construct){
   while(true)
   {
      if(!ord("\x02"))
      {
         if(!ord("\x02"))
         {
            break;
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
      if(!ord("\x06"))
      {
         §§pop()[§§pop()] = §§pop();
      }
      backgroundDown = "ButtonCloseDown";
      backgroundUp = "ButtonCloseUp";
      enabled = true;
      icon = "";
      §§push("label");
      §§push("");
      if(!getTimer())
      {
         §§push(getProperty(§§pop(), _X));
      }
      else
      {
         addr2cf56:
         set(§§pop(),§§pop());
         set(§§constant(8),false);
         set(§§constant(9),§§constant(10));
         set(§§constant(11),false);
      }
      return;
   }
   §§goto(addr2cf56);
}
