on(construct){
   while(true)
   {
      if(!ord("\b"))
      {
         if(false)
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
      autoLoad = true;
      set("\x18\x02\x1d",0);
      enabled = false;
      forceReload = false;
      set("\x16\x04\x04","StaticR");
      §§push("colors");
      §§push("-1,-1,-1");
      if(!getTimer())
      {
         §§goto(addr221a3);
      }
      break;
   }
   set(§§pop(),§§pop());
   accessories = "0,0,0,0";
   scaleContent = true;
   flip = false;
   styleName = "none";
   addr221a3:
   §§pop()(§§pop());
}
