on(construct){
   while(true)
   {
      if(!(0x22464A4B & 0x22464A4B))
      {
         if(!(true or true))
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
         autoLoad = true;
         centerContent = false;
         contentPath = "clips/maps/hints.swf";
         enabled = false;
         fallbackContentPath = "";
         §§push("forceReload");
         §§push(false);
         if(!(getTimer() + 1))
         {
            §§pop()[§§pop()] = §§pop();
            §§goto(addr1e42f);
         }
      }
      set(§§pop(),§§pop());
      break;
   }
   scaleContent = false;
   styleName = "default";
   addr1e42f:
}
